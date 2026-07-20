from elm327 import ELM327
from parser import parse_response

class OBD:
    def __init__(self):
        self.conn = ELM327()

    def get_rpm(self):
        resp = self.conn.send("010C")
        return parse_response("010C", resp)

    def get_speed(self):
        resp = self.conn.send("010D")
        return parse_response("010D", resp)

    def get_coolant_temp(self):
        resp = self.conn.send("0105")
        return parse_response("0105", resp)

    def get_dtc(self):
        resp = self.conn.send("03")
        return self._parse_dtc(resp)

    def clear_dtc(self):
        resp =  self.conn.send("04")
        if  "44" in resp.upper():
            return True
        return False
    
    def fuel_system_status(self):
        resp=self.conn.send("0103")
        return parse_response("0103")
    
    def get_fuel_pressure(self):
        resp=self.conn.send("010A")
        return parse_response("010A")
    
    def get_maf_airflow_rate(self):
        resp=self.conn.send("0110")
        return parse_response("0110")
    
    O2_PIDS = {
        1: "0114", 2: "0115", 3: "0116", 4: "0117",
        5: "0118", 6: "0119", 7: "011A", 8: "011B"
    }
    
    def get_oxygen(self, sensor_num):
        
        pid = self.O2_PIDS.get(sensor_num)
        if not pid:
            raise ValueError(f"Invalid O₂ sensor number: {sensor_num}")
        return self._query(pid)
    
    
    

        
