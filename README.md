## Regra de descoberta DCM D9902

Requisitos:
#
 /etc/zabbix/zabbix_server.conf
  
No arquivo de configuração do zabbix_server deixe ativado o ***StartTrappers*** e configure quantas intancias julgue necessário.
<pre> StartTrappers = 20 </pre>

## Como usar:

- coloque os dois scripts em qualquer lugar do  servidor que desejar e utilize o script para configurar o DCM <blockquote>**lld_dcm_zabbix.py**</blockquote>
- cada dcm precisa ter um arquivo separado, então caso deseje adionar mais de um dcm na regra de descoberta, copie varias vezes essse arquivo alterando somente o ip do dcm
- 

