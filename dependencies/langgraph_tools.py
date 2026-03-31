import re
import requests
from langchain.tools import tool
import langchain_core


@tool("Retrieve information based on IPv4 or Hostname")
def get_asset_info_by_ip(host: str) -> str:
  """
  Get information about host by hostname or IP. Args: IPv4 address or hostname. Results: Comprehensive data report about host.
  """
  try:
    # URL вашей системы инвентаризации/CMDB
    api_url = "https://msk01-rvp-r1337/assets?page_size=100"
    # Параметры запроса
    if re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', host) != None:
      params = {"ip": f'{host}'}
    else:
      params = {"name": f'{host}'}
    # Делаем GET-запрос
    response = requests.get(
                    api_url,
                    params=params,
                    verify=False
                    )
    # Проверяем статус
    if response.status_code == 200:
      raw_data = (response.json()).get("results")[0]
      # Форматируем ответ для агента
      # brother I hardcode that for a while
      data = {
      "Имя хоста": raw_data.get("name"),
      "ОС": raw_data.get("os"),
      "Тип": raw_data.get("type"),
      "IP адрес": raw_data.get("ip"),
      "Маска сети": raw_data.get("mask"),
      "MAC адрес": raw_data.get("mac"),
      "Домен": raw_data.get("domain"),
      "Active Directory расположение": raw_data.get("path_ad"),
      "Виртуальная машина": raw_data.get("virtual_machine"),
      "CPU модель": raw_data.get("cpu_name"),
      "Установлен антивирус": raw_data.get("antivirus"),
      "Дата установки антивируса": raw_data.get("antivirus_date"),
      "Состояние антивируса": raw_data.get("antivirus_state_details"),
      "Название антивируса": raw_data.get("antivirus_name"),
      "SCCM включен": raw_data.get("sccm_enabled"),
      "Находится в Active Directory": raw_data.get("ad_enabled"),
      "Географическое расположение хоста": raw_data.get("location_address"),
      "Связанные контакты": raw_data.get("contacts"),
      "Департамент": raw_data.get("departments"),
      "Источник Kaspersky Security Center": raw_data.get("ksc_source"),
      "Подсеть": raw_data.get("network"),
      "ANSIBLE включен": raw_data.get("ansible_enabled"),
      "Последняя дата входа с Active Directory": raw_data.get("ad_last_logon"),
      "CECMDB включен": raw_data.get("cecmdb_enabled"),
      "Kaspersky Anti Target Attack platform включен": raw_data.get("kata_enabled"),
      "Kaspersky Unified Monitoring and Analysis включен": raw_data.get("kuma_enabled"),
      "Версия агента Kaspersky Security Center": raw_data.get("ksc_agent_version"),
      "Версия антивируса Kaspersky Security Center": raw_data.get("ksc_antivirus_version"),
      "Последняя дата связанного события в SEMAS": raw_data.get("semas_last_event_datetime"),
      "CECMDB VM платформа": raw_data.get("cecmdb_vm_platform"),
      "CECMDB VM V-центр": raw_data.get("cecmdb_vm_vcenter"),
      "CECMDB VM кластер": raw_data.get("cecmdb_vm_cluster"),
      "CECMDB комментарий": raw_data.get("cecmdb_comments")
      }
      result = f"""Информация об объекте : {data}"""
      print(result)
      return result
    else:
      return f"Объект с IP {ip_address} не найден в системе инвентаризации"
  except:
      return "Ошибка: неверный формат JSON в файле"
  

def get_tools():
  current_state = list(globals())
  tools_list = list()
  for name in current_state:
    if isinstance(globals()[name], langchain_core.tools.structured.StructuredTool):
      tools_list.append(globals()[name])
  return tools_list
