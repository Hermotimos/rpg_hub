from django.core.mail import send_mail

from rpg_project import settings
from users.models import Profile


def send_mails_inform_location(request, location, informed_ids):
    profile = request.user.profile
    subject = f"[RPG] {profile} opowiedział Ci o nowym miejscu!"
    message = f"{profile} opowiedział Ci o miejscu zwanym:" \
              f" '{location.name}'.\n" \
              f"Informacje zostały zapisane w Twoim Toponomikonie: \n" \
              f"{request.build_absolute_uri()}"
    
    sender = settings.EMAIL_HOST_USER
    receivers = [
        p.user.email for p in Profile.objects.filter(id__in=informed_ids)
    ]
    if profile.status != 'gm':
        receivers.append('lukas.kozicki@gmail.com')
    send_mail(subject, message, sender, receivers)
    

def send_mails_inform_kn_packet(request, kn_packet, informed_ids):
    profile = request.user.profile
    subject = f"[RPG] {profile} przekazał Ci wiedzę: '{kn_packet.title}'"
    message = f"'{kn_packet.title}'.\n" \
              f"Więdzę tę możesz odnaleźć pod umiejętnością/ami:" \
              f" {', '.join(s.name for s in kn_packet.skills.all())}" \
              f" w zakładce Almanach: \n" \
              f"{request.get_host()}/knowledge/almanac/"
    
    sender = settings.EMAIL_HOST_USER
    receivers = [
        p.user.email for p in Profile.objects.filter(id__in=informed_ids)
    ]
    if profile.status != 'gm':
        receivers.append('lukas.kozicki@gmail.com')
    send_mail(subject, message, sender, receivers)
