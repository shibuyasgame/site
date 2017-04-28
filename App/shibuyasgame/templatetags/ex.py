from django import template

register = template.Library()


@register.simple_tag
def boost(item_atk, char_atk, brand, boosted_brands):
    atk = item_atk + char_atk
    if brand in boosted_brands:
        atk = 1.5*atk
    return str(atk) + " ATK"

@register.simple_tag
def cleanup(hp_val, atk_val, def_val):
    ans = ""
    if hp_val != 0:
        if hp_val > 0:
            ans = ans + "+"
        ans = ans + str(hp_val) + " HP, "
    if atk_val != 0:
        if atk_val > 0:
            ans = ans + "+"
        ans = ans + str(atk_val) + "ATK, "
    if def_val != 0:
        if def_val > 0:
            ans = ans + "+"
        ans = ans + str(def_val) + "DEF, "
    if len(ans) > 2:
        return ans[0:-2]
    return ""

@register.simple_tag
def thread_calc(hp_val, atk_val, def_val, bonus_hp, bonus_atk, bonus_def, condition, pronouns):
    hp_val = hp_val
    if condition == pronouns:
        hp_val = hp_val + bonus_hp
        atk_val = atk_val + bonus_atk
        def_val = def_val + bonus_def
    return cleanup(hp_val, atk_val, def_val)
