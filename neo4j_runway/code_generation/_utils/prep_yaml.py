import yaml


def prep_yaml() -> None:

    class folded_unicode(str):
        pass

    class literal_unicode(str):
        pass

    def folded_unicode_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=">")

    def literal_unicode_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")

    yaml.add_representer(folded_unicode, folded_unicode_representer)
    yaml.add_representer(literal_unicode, literal_unicode_representer)
