## Regra de descoberta DCM D9902

Requisitos:
#
 /etc/zabbix/zabbix_server.conf
  
No arquivo de configuração do zabbix_server deixe ativado o ***StartTrappers*** e configure quantas intancias julgue necessário.
<pre> StartTrappers = 20 </pre>

## Como usar:

- coloque os dois scripts em qualquer lugar do  servidor que desejar e utilize o script para configurar o DCM <blockquote>**lld_dcm_zabbix.py**</blockquote>

- cada DCM precisa ter um arquivo separado, então caso deseje adionar mais de um DCM na regra de descoberta, copie varias vezes essse arquivo alterando somente o ip do DCM
  
- importe a template para o zabbix, crie seu host e associe a template.
  
- Após criar os arquivos com o nome que preferir, execute a primeira função para criar todos os itens e triggers:
  <blockquote> dcm_trapper = descobrir_dcm("IP DO DCM",host_dcm,"IP DO ZABBIX") </blockquote>

- Depois da criação dos itens e se caso estiver tudo correto, comente a primera função e descomente a segunda para enviar os valores para as chaves dos itens criados.
  <blockquote> dcm_values = enviar_valores_zabbix("IP DO DCM",host_dcm,"IP DO ZABBIX") </blockquote>

- e por fim coloque o script unico de cada dcm para ser executado na cron do linux
 <blockquote> crontab -e </blockquote>
 <blockquote> */3 * * * * /usr/bin/python3 /home/scripts/dcm_1.py </blockquote>

 **A cada 3 minutos será enviado os valores para os canais**

  


