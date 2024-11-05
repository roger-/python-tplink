import httpx
import hashlib
import datetime


class TPLinkRouterBase:
    URL_BASE = 'http://{host}'
    PATH_LOGIN = '/'
    PATH_COOKIE = '/'

    def __init__(self, host, username, password):
        self.username = username
        self.password = password
        
        base_url = self.URL_BASE.format(host=host)
        headers = {
            'Referer': base_url
        }
        self.session = httpx.AsyncClient(verify=False,
            headers=headers,
            base_url=base_url)

    async def get_data(self, path, **extra_params):
        # timestamp needed for certain devices
        timestamp = int(datetime.datetime.now().timestamp() * 1e3)
        params = {**extra_params, "_": timestamp}

        # send request and verify response
        response = await self.session.get(path, params=params)

        assert(response.status_code == 200)
        js = response.json()
        assert(js['success'] == True)

        return js['data']

    async def login(self):
        # get cookie
        response = await self.session.get(self.PATH_COOKIE)

        # make and send login data
        login_data = self._make_login_params(response.cookies)
        response = await self.session.post(self.PATH_LOGIN, data=login_data)
        assert(response.status_code == 200)

        return self

    def _make_login_params(self, cookie):
        raise NotImplementedError

    async def close(self):
        await self.session.aclose()





