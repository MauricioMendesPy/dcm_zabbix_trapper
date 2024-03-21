#####################################################################################
#----------------SCRIPT DE DESCOBERTA DE PORTAS DO DCM CISCO D9902------------------#
#-------------------------- INPUT DE CANAIS-----------------------------------------#
#                                                                                   #
#                       CRIADO POR MAURICIO MENDES SOARES                           #
#             QUALQUER DUVIDA - 13 991378882 - MAURICIO.SOARES@CLARO.COM.BR         #
#                                                                                   #
#                    Não RETIRE OS CRéDITOS POR GENTILEZA                           #
#####################################################################################


import subprocess
import re
import json
import shlex

# Função para buscar dados do DCM usando SNMP
def obter_oids_dcm(ip):
    try:
        results = subprocess.check_output(['snmpwalk', '-v', '2c', '-c', 'public', ip,
                                           '.1.3.6.1.4.1.1482.20.3.2.2.3.1.1.10.1.3'], timeout=300)
        decode = str(results.decode('utf-8')).splitlines()

        # Separar a OID e seu valor
        dcm_data = {}
        for linha in decode:
            oid_valor = linha.split('=')
            if len(oid_valor) == 2:
                oid, valor = oid_valor
                dcm_data[oid.strip()] = valor.strip()

        # Converter valores hexadecimais para ISO-8859-1
        dcm_updated = {}
        for oid, valor in dcm_data.items():
            if 'Hex-STRING:' in valor:
                valor_hex = valor.split('Hex-STRING:')[1].strip()
                decoded_string = bytes.fromhex(valor_hex).decode('ISO-8859-1')
                dcm_updated[oid] = decoded_string
            else:
                dcm_updated[oid] = valor.strip('STRING: ')

        return dcm_updated
    except subprocess.CalledProcessError as e:
        print(f'Erro ao obter dados do DCM: {e}')
        return {}
    except subprocess.TimeoutExpired:
        print('Tempo limite expirado ao obter dados do DCM.')
        return {}
    except Exception as e:
        print(f'Ocorreu um erro inesperado: {e}')
        return {}

# Função para encontrar portas no DCM e agrupá-las com suas macros
def encontrar_portas(ip):
    dcm_data = obter_oids_dcm(ip)
    porta_dict = {}

    for dados, valores in dcm_data.items():
        match = re.search(r'\.(\d)\d{5,}', dados)
        if match:
            porta = int(match.group(1))
            sid = re.findall(r'\.\d{1,}$', dados)
            sid_canal = "".join(sid).strip('.')
            if porta not in porta_dict:
                porta_dict[porta] = []
            porta_dict[porta].append({
                "{#OID}": dados,
                "{#CANAL}": valores.strip('"'),
                "{#SID}": sid_canal
            })

    return porta_dict

# Função para enviar status dos itens para o Zabbix
def enviar_valores(ip, porta_dcm, host,ip_zabbix):
    try:
        results = subprocess.check_output(['snmpwalk', '-v', '2c', '-c', 'public', ip,
                                           '.1.3.6.1.4.1.1482.20.3.2.2.3.1.1.10.1.4'], timeout=300)
        decode = str(results.decode('utf-8')).splitlines()

        items_status_dict = {}
        for linha in decode:
            oid_valor = linha.split('=')
            if len(oid_valor) == 2:
                oid, valor = oid_valor
                items_status_dict[oid.strip()] = valor.strip().strip('INTEGER: ')

        dcm_status = encontrar_portas(ip)

        for oids, status in items_status_dict.items():
            for porta, valores in dcm_status.items():
                if porta == porta_dcm:
                    for values in valores:
                        padrao = r'\d+\.\d+$'
                        oid_extraida_dcm_string = re.search(padrao, values['{#OID}'])
                        oid_extraida_status = re.search(padrao, oids)
                        if oid_extraida_dcm_string and oid_extraida_status and oid_extraida_dcm_string.group() == oid_extraida_status.group():
                            chave = oid_extraida_status.group()
                            padrao_chave = r'\.\d{1,}'
                            chave_zabbix = re.search(padrao_chave, chave).group().strip('.')
                            if values['{#OID}'] not in values:
                                values['{#CHAVE}'] = f"P{porta_dcm}_SID_[{chave_zabbix}]"
                                values['{#STATUS}'] = status

                                comando = f'zabbix_sender -z {ip_zabbix} -s {host} -k {values["{#CHAVE}"]} -o {values["{#STATUS}"]}'
                                try:
                                    resultado = subprocess.check_output(comando, shell=True, timeout=300)
                                    print(f'Dados enviados com sucesso: {resultado.decode()}')
                                except subprocess.CalledProcessError as e:
                                    print(f'Erro ao enviar dados para o Zabbix: {e}')
    except subprocess.CalledProcessError as e:
        print(f'Erro ao obter dados do DCM: {e}')
    except subprocess.TimeoutExpired:
        print('Tempo limite expirado ao obter dados do DCM.')
    except Exception as e:
        print(f'Ocorreu um erro inesperado: {e}')

# Função para criar regras de portas no Zabbix
def criar_lld(ip, porta_dcm, host, chave,ip_zabbix):
    dcm = encontrar_portas(ip)

    dados_json = []
    for porta, valores in dcm.items():
        if porta == int(porta_dcm):
            for valor in valores:
                dados_json.append({
                    "{#CANAL}": valor["{#CANAL}"],
                    "{#SID}": valor["{#SID}"],
                    "{#OID}": valor["{#OID}"]
                })

    # Convertendo para formato JSON válido
    json_dcm = json.dumps(dados_json).replace("'", "//'")
    json_dcm_quote = shlex.quote(json_dcm)

    # Envia as informações do DCM para o Zabbix
    criar_regra = f'zabbix_sender -z {ip_zabbix} -s {host} -k {chave} -o {json_dcm_quote}'
    try:
        resultado = subprocess.check_output(criar_regra, shell=True, timeout=300)
        print(f'Dados enviados com sucesso: {resultado.decode()}')
    except subprocess.CalledProcessError as e:
        print(f'Erro ao enviar dados para o Zabbix: {e}')
    except subprocess.TimeoutExpired:
        print('Tempo limite expirado ao enviar dados para o Zabbix.')
    except Exception as e:
        print(f'Ocorreu um erro inesperado: {e}')

# Função principal para descobrir DCMs
def descobrir_dcm(ip, host_dcm,ip_zabbix):
    dcm_ports = encontrar_portas(ip)

    for porta in dcm_ports:
        criar_lld(ip, porta, host_dcm, f"PORTA_{porta}",ip_zabbix)

#Função para enviar os valores para o Zabbix
def enviar_valores_zabbix(ip,host_dcm,ip_zabbix):
    dcm_ports = encontrar_portas(ip)

    for portas in dcm_ports:
        send_itens = enviar_valores(ip,portas,host_dcm,ip_zabbix)


