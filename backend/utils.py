"""
Utilitários auxiliares
"""
from datetime import datetime, timedelta
import re

def parse_relative_date(date_str: str, time_str: str = "00:00") -> tuple:
    """
    Converte datas relativas em datas absolutas
    
    Args:
        date_str: String como "amanhã", "hoje", "15/01/2024"
        time_str: String como "10:00" ou "10h"
        
    Returns:
        Tupla (start_time, end_time) em formato ISO 8601
    """
    now = datetime.now()
    
    # Parse do horário
    time_match = re.search(r'(\d{1,2}):?(\d{2})?', time_str)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
    else:
        hour = 10
        minute = 0
    
    # Parse da data
    date_str_lower = date_str.lower()
    
    if "hoje" in date_str_lower:
        target_date = now
    elif "amanhã" in date_str_lower or "amanha" in date_str_lower:
        target_date = now + timedelta(days=1)
    elif "depois de amanhã" in date_str_lower:
        target_date = now + timedelta(days=2)
    else:
        # Tentar parse de data específica
        try:
            # Formato DD/MM/YYYY
            if "/" in date_str:
                parts = date_str.split("/")
                if len(parts) == 3:
                    target_date = datetime(int(parts[2]), int(parts[1]), int(parts[0]))
                else:
                    target_date = now
            else:
                target_date = now
        except:
            target_date = now
    
    # Criar datetime completo
    start_datetime = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    # End datetime é 1 hora depois (padrão)
    end_datetime = start_datetime + timedelta(hours=1)
    
    # Converter para ISO 8601
    start_iso = start_datetime.isoformat()
    end_iso = end_datetime.isoformat()
    
    return start_iso, end_iso

