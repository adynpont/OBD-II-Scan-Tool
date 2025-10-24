from .connection import ELMConnection
from .parser import parse_response

class OBD:
    def __init__(self):
        self.conn = ELMConnection()

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
        return self.conn.send("03")

    def clear_dtc(self):
        return self.conn.send("04")
    
    def fuel_system_status(self):
        resp=self.conn.send("0103")
        return parse_response("0103")
    
    def get_fuel_pressure(self):
        resp=self.conn.send("010A")
        return parse_response("010A")
    
    def get_maf_airflow_rate(self):
        resp=self.conn.send("0110")
        return parse_response("0110")
    
    def get_oxygen1(self):
        resp=self.conn.send("0114")
        return parse_response("0114")
    
    def get_oxygen2(self):
        resp=self.conn.send("0115")
        return parse_response("0115")
    
    def get_oxygen3(self):
        resp=self.conn.send("0116")
        return parse_response("0116")
    
    def get_oxygen4(self):
        resp=self.conn.send("0117")
        return parse_response("0117")
    
    def get_oxygen5(self):
        resp=self.conn.send("0118")
        return parse_response("0118")
    
    def get_oxygen6(self):
        resp=self.conn.send("0119")
        return parse_response("0119")

        
