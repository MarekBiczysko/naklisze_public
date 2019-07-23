from django.utils.translation import ugettext_lazy as _


STRAP_MODEL_CHOICES = (
    ('rope', _('sznurowany')),
    ('leather_thin_black', _('skórzany cienki czarny')),
    ('leather_thin_brown', _('skórzany cienki brązowy')),
    ('leather_medium_black', _('skórzany średni czarny')),
    ('leather_medium_brown', _('skórzany średni brązowy')),
    ('leather_thick_black', _('skórzany gruby czarny')),
    ('leather_thick_brown_dark', _('skórzany gruby ciemny brązowy')),
    ('leather_thick_brown_light', _('skórzany gruby jasny brązowy')),
)

STRAP_TYPE_CHOICES = (
    ('wrist', _('Nadgarstkowy')),
    ('head', _('Na szyję')),
)

STRAP_DESCRIPTION_PL = """ \
Pasek nadgarstkowy pasuje do wszystkich aparatów posiadających oczko do jego zamocowania.
Zapewnia wygodę i komfort trzymania aparatu, przydatny w szczególności przy fotografii ulicznej.
Retro design pasuje także to nowoczesnych typów aparatów.
"""

STRAP_DESCRIPTION_EN = """ \
The strap fits all cameras with mount for fixing it.
It provides convenience and comfort of holding the camera, especially useful during street photography.
Retro design matches with modern camera types.
"""
