{% set event_data = data['data'] %}

ifdown_workflow:
  runner.tshoot.ifdown:
    - host: {{ event_data['minion'] }}
    - origin_ip: {{ event_data['origin_ip'] }}
    - yang_message: {{ event_data['yang_message'] }}
    - error: {{ event_data['error'] }}
    - tag: {{ event_data['tag'] }}
    - current_case: {{ event_data['case'] }}

