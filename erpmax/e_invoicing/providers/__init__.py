from frappe import _


COUNTRY_PROVIDER_MAP = {
    "SA": "zatca",
    "EG": "eta",
    "AE": "fta",
    "JO": "istd",
    "BH": "nbr",
    "KW": "kuwait",
    "OM": "oman",
    "MA": "dgi",
}

PROVIDER_MODULE_MAP = {}


def get_provider(provider_type):
    provider_type = provider_type.lower()
    if provider_type in PROVIDER_MODULE_MAP:
        return PROVIDER_MODULE_MAP[provider_type]

    if provider_type == "zatca":
        from .zatca import ZATCAProvider
        PROVIDER_MODULE_MAP[provider_type] = ZATCAProvider
    elif provider_type == "eta":
        from .eta import ETAProvider
        PROVIDER_MODULE_MAP[provider_type] = ETAProvider
    elif provider_type == "fta":
        from .fta import FTAProvider
        PROVIDER_MODULE_MAP[provider_type] = FTAProvider
    else:
        raise ValueError(_("Unsupported provider type: {0}").format(provider_type))

    return PROVIDER_MODULE_MAP[provider_type]


def get_provider_for_country(country_code):
    provider_key = COUNTRY_PROVIDER_MAP.get(country_code.upper())
    if not provider_key:
        raise ValueError(_("No provider mapped for country code: {0}").format(country_code))
    provider_class = get_provider(provider_key)
    return provider_class()
