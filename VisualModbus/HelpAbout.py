# import build-in modules
import PySimpleGUI as sg

VERSION_MAJOR = 0

VERSION_MINOR = 1

VERSION_BUILD = 8

VERSION = "{}.{}.{}".format(VERSION_MAJOR, VERSION_MINOR, VERSION_BUILD)

RELEASE_NOTE_9 = "2020/01/31 - 0.1.8 - \n"\
                 " - Fix podpory čtení a zápisu stringů \n" \
                 " - Přidáno tlačítko Write All, které zapíše všechny holding registry"\

RELEASE_NOTE_8 = "2020/01/25 - 0.1.7 - \n"\
                 " - Status ukazuje jenom 1 poslední záznam, log přesunut do okna\n"\
                 " - Info tlačítko s popisem všech parametrů registru\n" \
                 " - Přidána políčka pro hodnoty registru v hexu, min a max \n"

RELEASE_NOTE_7 = "2019/11/25 - 0.1.6  \n" \
                 " - Opakovaná Write operace i bez změny hodnot\n" \
                 " - Parametrizace minimální mezi-znakové mezery\n" \
                 " - V případě zavřeného socketu se ho snaží opět otevřít\n" \
                 " - Fix zápisu krátkých floatů\n" \
                 " - Fix update firmware na vyšší adresy"

RELEASE_NOTE_6 = "2019/10/20 - 0.1.5  \n" \
                 " - Nová procedura upgradu firmware s proměnnou velikostí stránky\n" \
                 " - Registrová mapa obsahuje minimum a maximum registrů"


RELEASE_NOTE_5 = "2019/10/13 - 0.1.4  \n" \
                 " - Konfigurace rozdelena do vice JSONu \n" \
                 " - Konfigurace se uklada rovnou v okne, mozno menit velikost okna" \

RELEASE_NOTE_4 = "2019/10/08 - 0.1.3  \n" \
                 " - Pridan upgrade firmwaru pres modbus \n" \
                 " - Konfiguracni json obsahuje hodnoty pro upgrade\n" \
                 " - Prvni nedokonala verze, bude se vylepsovat" \


RELEASE_NOTE_3 = "2019/09/22 - 0.1.2  \n" \
                 " - Registrova mapa nemusi byt kompaktni, mohou byt vynechane adresy" \


RELEASE_NOTE_2 = "2019/09/21 - 0.1.1  \n" \
                 " - Pridano nastaveni, ktere lze ulozit a nacist z jsonu\n" \
                 " - Zapis vice registru naraz je mozny \n" \
                 " - Viceradkovy status, pridan datum, premisten na stranu\n" \
                 " - Pribylo okno Help->About"

RELEASE_NOTE_1 = "2019/09/14 - 0.0.0 - \n" \
                 " - Prvni nedokonala verze"

NOTES = [RELEASE_NOTE_1, RELEASE_NOTE_2, RELEASE_NOTE_3, RELEASE_NOTE_4, RELEASE_NOTE_5, RELEASE_NOTE_6,
         RELEASE_NOTE_7, RELEASE_NOTE_8, RELEASE_NOTE_9]


def show_help():
    """Create new window containing help text"""
    layout = [[sg.Text("\n".join(reversed(NOTES)), key="ABOUT", auto_size_text=True, pad=(5, 5))],
              [sg.Submit("CLOSE")]]
    window = sg.Window('Help - About', layout, disable_close=True, resizable=True, auto_size_text=True,
                       auto_size_buttons=True)
    window.read()
    window.close()

