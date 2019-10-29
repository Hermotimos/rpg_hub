
def create_sorting_name(obj):
    name = str(obj)
    name = name.replace('Ą', 'AĄ')
    name = name.replace('ą', 'aą')
    name = name.replace('Ć', 'CĆ')
    name = name.replace('ć', 'cć')
    name = name.replace('Ę', 'EĘ')
    name = name.replace('ę', 'eę')
    name = name.replace('Ł', 'LŁ')
    name = name.replace('ł', 'lł')
    name = name.replace('Ó', 'OÓ')
    name = name.replace('ó', 'oó')
    name = name.replace('Ś', 'SŚ')
    name = name.replace('ś', 'sś')
    name = name.replace('Ź', 'ZŻ')
    name = name.replace('ż', 'zż')
    name = name.replace('Ż', 'ZŹ')
    name = name.replace('ż', 'zź')
    return name



# def create_sorting_name(obj):
#     name = str(obj)
#     name = name.replace('Ą', 'Azz')
#     name = name.replace('ą', 'azz')
#     name = name.replace('Ć', 'Czz')
#     name = name.replace('ć', 'czz')
#     name = name.replace('Ę', 'Ezz')
#     name = name.replace('ę', 'ezz')
#     name = name.replace('Ł', 'Lzz')
#     name = name.replace('ł', 'lzz')
#     name = name.replace('Ó', 'Ozz')
#     name = name.replace('ó', 'ozz')
#     name = name.replace('Ś', 'Szz')
#     name = name.replace('ś', 'szz')
#     name = name.replace('Ź', 'Zzz')
#     name = name.replace('ż', 'zzz')
#     name = name.replace('Ż', 'Zzz')
#     name = name.replace('ż', 'zzz')
#     return name
