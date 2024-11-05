from .base import TPLinkRouterBase
import hashlib
from sg_parser import parse_script_variables


# Support for TL-SG108E

PATH_LOGIN = '/logon.cgi'
PATH_SYS_INFO = '/SystemInfoRpm.htm'
PATH_PORT_STATS = '/PortStatisticsRpm.htm'
PATH_PORT_SETTINGS = '/PortSettingRpm.htm'
PATH_IP_SETTINGS = '/IpSettingRpm.htm'
PATH_LED_STATUS = '/TurnOnLEDRpm.htm'
PATH_LED_SET = '/led_on_set.cgi'
PATH_REBOOT = '/reboot.cgi'


class TPLinkSG(TPLinkRouterBase):
    URL_BASE = 'http://{host}'
    PATH_LOGIN = PATH_LOGIN

    def _make_login_params(self, cookies):
        login_data = {"username": self.username, "password": self.password, "cpassword": "", "logon": "Login"}

        return login_data
    
    async def get_data(self, path, **extra_params):
        response = await self.session.get(path, params=extra_params)
        assert(response.status_code == 200)

        vars = parse_script_variables(response.text)
        vars.pop('tip') # this always seems to be empty

        return vars
    
    async def port_stats(self):
        data = await self.get_data(PATH_PORT_STATS)

        return data

    async def led_status(self) -> bool:
        data = await self.get_data(PATH_LED_STATUS)

        return bool(data['led'])
    
    async def set_led(self, val):
        data = await self.get_data(PATH_LED_SET, rd_led=int(val), led_cfg='Apply')

        return bool(data['led'])
    
    async def ip_settings(self):
        data = await self.get_data(PATH_IP_SETTINGS)

        output = flatten_dict(data['ip_ds'])

        return output
    
    async def port_settings(self):
        data = await self.get_data(PATH_PORT_SETTINGS)

        return data
    
    async def device_info(self):
        data = await self.get_data(PATH_SYS_INFO)

        output = flatten_dict(data['info_ds'])

        return output
    
    async def reboot(self):
        data = dict(reboot_op="reboot", save_op=1, apply="Reboot")
        response = await self.session.post(PATH_REBOOT, data=data)
        assert(response.status_code == 200)

def flatten_dict(data):
    output = {}

    for k in data:
        output[k] = data[k][0] if isinstance(data[k], (list, tuple)) and len(data[k]) == 1 else data[k]

    return output

async def main():
    import json

    with open("../secrets_tpl.json") as handle:
        login = json.load(handle)
        
    tpl = await TPLinkSG('192.168.0.23', **login).login()

    devinfo = await tpl.device_info()
    print(json.dumps(devinfo, indent='  '))

    data = await tpl.port_settings()
    print(json.dumps(data, indent='  '))

    data = await tpl.port_stats()
    print(json.dumps(data, indent='  '))



if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
