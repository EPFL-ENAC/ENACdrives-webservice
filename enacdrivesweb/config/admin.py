from django.contrib import admin

from .models import User, EpflUnit, LdapGroup, Config


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    fieldsets = (
        ("What", {"fields": (("name", "enabled"), "rank", "data")}),
        ("Who", {"fields": ("category", "users", "epfl_units", "ldap_groups")}),
        (
            "Client Filter",
            {
                "fields": (
                    "client_filter_version",
                    "client_filter_os",
                    "client_filter_os_version",
                )
            },
        ),
    )
    list_display = (
        "name",
        "enabled",
        "rank",
        "category",
        "get_users",
        "get_epfl_units",
        "get_ldap_groups",
        "get_client_filter",
        "get_data",
    )
    list_display_links = ("name", "get_data")
    ordering = ("rank",)

    @admin.display(
        description="Users"
    )
    def get_users(self, obj):
        if obj.category == Config.CAT_USER:
            html = "<span>{}</span>"
        else:
            html = "<span class='field-off red'>{}</span>"
        return html.format(", ".join([u.name for u in obj.users.all()]))


    @admin.display(
        description="EPFL Units"
    )
    def get_epfl_units(self, obj):
        if obj.category == Config.CAT_EPFL_UNIT:
            html = "<span>{}</span>"
        else:
            html = "<span class='field-off red'>{}</span>"
        return html.format(", ".join([g.name for g in obj.epfl_units.all()]))


    @admin.display(
        description="Ldap Groups"
    )
    def get_ldap_groups(self, obj):
        if obj.category == Config.CAT_LDAP_GROUP:
            html = "<span>{}</span>"
        else:
            html = "<span class='field-off red'>{}</span>"
        return html.format(", ".join([g.name for g in obj.ldap_groups.all()]))


    @admin.display(
        description="Data"
    )
    def get_data(self, obj):
        return obj.data.replace("\n", "<br/>")


    @admin.display(
        description="Client Filter"
    )
    def get_client_filter(self, obj):
        the_list = []
        html = "<span>{}</span>"
        if obj.client_filter_version != "":
            the_list.append(
                "<nobr>version is '{}'</nobr>".format(obj.client_filter_version)
            )
        if obj.client_filter_os != "":
            the_list.append("<nobr>os is '{}'</nobr>".format(obj.client_filter_os))
        if obj.client_filter_os_version != "":
            the_list.append(
                "<nobr>os_version is '{}'</nobr>".format(obj.client_filter_os_version)
            )
        if len(the_list) == 0:
            html = "<span class='field-off'>{}</span>"
            the_list.append("None")
        return html.format(" and <br>".join(the_list))


    def short(self, string, max_length):
        if len(string) > max_length:
            return string[: max_length - 3] + "..."
        else:
            return string

    class Media:
        css = {"all": ("css/configadmin_custom.css",)}
        js = ("js/configadmin_custom.js",)


admin.site.register(User)
admin.site.register(EpflUnit)
admin.site.register(LdapGroup)
