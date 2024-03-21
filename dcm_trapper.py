from lld_dcm_zabbix import enviar_valores_zabbix,descobrir_dcm

#ESSE NOME DO DCM DEVE SER IDENTICO AO DO ZABBIX
host_dcm = "NOME DO SEU DCM"

#CRIAÇÃO DA REGRA --------------------
#APÓS EXECUTAR A FUNÇÃO DE DESCOBRIR O DCM, COMENTE ESSA LINHA PARA ENVIAR OS VALORES PARA OS ITENS
dcm_trapper = descobrir_dcm("IP DO DCM",host_dcm,"IP DO ZABBIX") 

#ENVIO DO STATUS PARA O ZABBIX
#DESCOMENTE ESSA LINHA APÓS A CRIAÇÃO DOS ITENS NO ZABBIX
#dcm_bert = enviar_valores_zabbix("IP DO DCM",host_dcm,"IP DO ZABBIX")
