
class ShopeeCallbackDto(dict):

    # Shopee用于获取AccessToken和RefreshToken
    code = ''
    # Shopee授权给开发者主账号main_account_id,当使用主账号授权时候返回
    main_account_id = ''
    # 非Shopee返回参数，Shopee授权时带上的base64加密参数，通过解密可获取partner_id,partner_key,username
    secret = ''

    __setattr__ = dict.__setitem__
    __getattribute__ = dict.__getitem__

    @staticmethod
    def dict_to_object(dict_data):
        if not isinstance(dict_data, dict):
            return dict_data
        inst = ShopeeCallbackDto()
        for k, v in dict_data.items():
            inst[k] = ShopeeCallbackDto.dict_to_object(v)
        return inst
