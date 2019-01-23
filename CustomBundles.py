# -----------------------------------------------------------------------
# <copyright file = "CustomBundles.py" company = "IGT">
#     Copyright © 2018 IGT.  All rights reserved.
# </copyright>
# -----------------------------------------------------------------------

import PySimpleGUI as sg
import os
import re
import zipfile
import package as pkg
# import threading
# todo implement a progress meter so the PA tester doesn't freak out while waiting for something to happen

chooser_package_list = []
package_list = []
listbox_tuple = ()
game_locations_list = []
add_game_button_label = 'Add game to game bundle list'
add_chooser_button_label = 'Add chooser to bundle list'
delete_chooser_button_label = 'Delete selected chooser'
delete_game_button_label = 'Delete selected game'

# todo remove the debug print statements

class FileNotFoundException(Exception):
    def __init__(self, file):
        self.file = file

    def __str__(self):
        error_string = "File not found: {0}".format(repr(self.file))
        return error_string


def create_empty_folder(folder_name):
    if not os.path.exists(folder_name):
        print("creating", folder_name)
        os.makedirs(folder_name)


def verify_path(path):
    """Verify that the path specified exists."""
    if not os.path.exists(path):
        raise FileNotFoundException(path)


def verify_paths():
    verify_path(game_bin)
    verify_path(host_bin)
    verify_path(bundle_target_dir)


def empty_dir(top):
    if (top == '/' or top == "\\"):
        return
    else:
        for root, dirs, files in os.walk(top, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))


def call_package(package_name, folder_path, description):
    if os.getcwd() is not folder_path:
        os.chdir(folder_path)

    pkg.not_main(package_name=package_name,
                 folder_path=folder_path,
                 description=description,
                 category='game',  # won't change for PA custom bundles
                 platform='avp'  # won't change for PA custom bundles, so don't bother making the user figure it out.
                 )
    return True


def list_to_tuple(listbox_contents): # put in format the user interface can understand
    listbox_tuple = ()
    for item in listbox_contents:
        listbox_tuple += (item,)

    return listbox_tuple


# ------ chooser package extraction ----------

def chooser_package():
    package_found_flag = False
    if len(chooser_package_list) > 0:
        for chooser_zip_file_found in chooser_package_list:
            if chooser_zip_file_found.endswith('zip'):
                print(bundle_target_dir, chooser_zip_file_found)

                with zipfile.ZipFile(chooser_zip_file_found, 'r') as zp:
                    for file in zp.namelist():
                        if re.search('\.package', file):
                            package_file_found = file
                            sg.Popup(package_file_found + ' found. Please wait, this takes a minute to copy...')
                            print('package file found is: ', file + '. Please wait, this takes a minute...')
                            zp.extract(package_file_found, path=bundle_target_dir)
                            package_found_flag = True
                            # break
        if package_found_flag:
            return True  # It's all good; everything is going according to plan
    else:
        print('No chooser package selected!')
        yes_no = sg.PopupYesNo('No chooser package selected - is this what you want?')
        if yes_no == 'Yes':
            print('Selected Yes to continue without a chooser package.')
            return True  # no chooser selected, but the user *really* wants to continue anyway. Who am I to disagree?
        else:
            print('Selected No to continue without a chooser package.')
            sg.Popup('No chooser package file selected. Click the [Browse] button to select a chooser zip file. ')
            return False  # good choice.  No chooser for a package is just nonsense


# -------- Game package extraction -------------

def game_package():
    package_found_flag = False  # assume the worst in people
    if len(package_list) > 0:
        for game_zip_found in package_list:
            if game_zip_found.endswith('zip'):
                print(bundle_target_dir, game_zip_found)

                with zipfile.ZipFile(game_zip_found, 'r') as zp:
                    for file in zp.namelist():
                        if re.search('\.package', file):
                            package_file_found = file
                            sg.Popup(
                                package_file_found +
                                ' found. Please wait, this takes a minute to copy... click ok to continue')
                            print('package file found is: ', file + '. Please wait, this takes a minute...')
                            zp.extract(package_file_found, path=bundle_target_dir)
                            package_found_flag = True  # faith in humanity is restored!
        if package_found_flag:
            sg.Popup('All requirements met, click OK to build bundle.')  # it's like a participation trophy
            return True
    else:
        print('No game package file selected!')
        yes_no = sg.PopupYesNo('No game package file selected - is this what you want?')
        if yes_no == 'Yes':
            print('Selected Yes to continue without a game package.')
            return True  # what can I say, some people...
        else:
            print('Selected No to try again.')
            sg.Popup('No chooser zip file selected. Click the [Browse] button to select a chooser zip file. ')
            return False  # try again until you get it right!


layout = [
    [sg.Text('Create a Custom Bundle')],
    [sg.Text('Game/bin directory', size=(15, 1)), sg.InputText("d:\\GameBin\\bin", do_not_clear=True)],  # values[0]
    [sg.Text('Host/bin directory', size=(15, 1)), sg.InputText("d:\\HostBin\\bin", do_not_clear=True)],  # values[1]
    [sg.Text('Bundle target dir', size=(15, 1)), sg.InputText("d:\\TheBundleTest", do_not_clear=True)],  # values[2]
    [sg.Text('--------------------------------------------------------------------------------------------------------------------------')],
    [sg.Text('Location of FI with Chooser package')],
    [sg.InputText('\\\\data\\shares\\PA\\Rel_AI_Boot\\AI\\AI020000L0001\\Image', do_not_clear=True), sg.FileBrowse()],  # values[3]
    [sg.Button(add_chooser_button_label, button_color=('white', 'green'))], [sg.Listbox(values=listbox_tuple, key='_CHOOSER_LISTBOX_', select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, size=(70, 4))],
    [sg.Button(delete_chooser_button_label,button_color=('white', 'red'))],
    [sg.Text('--------------------------------------------------------------------------------------------------------------------------')],
    [sg.Text('Location of game package')],
    [sg.InputText('\\\\engfile6\\pa\\Inbox\\GI020001H2RB001_1\\Image', do_not_clear=True), sg.FileBrowse()],
    # values[4]
    [sg.Button(add_game_button_label, button_color=('white', 'green'))], [sg.Listbox(values=listbox_tuple, key='_LISTBOX_', select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, size=(70, 4))],
    [sg.Button(delete_game_button_label, button_color=('white', 'red'))],
    [sg.Text('--------------------------------------------------------------------------------------------------------------------------')],
    [sg.Text('Bundle Name', size=(15, 1)), sg.InputText("ASGB020M2xxxxx", do_not_clear=True)],  # values[5]
    [sg.Text('Bundle Description', size=(15, 1)), sg.InputText("These words describe my bundle.", do_not_clear=True)], # values[6]
    [sg.Submit(button_color=('black', 'lightgreen')), sg.Exit(button_color=('black', 'Crimson'))]
]
window = sg.Window('Create a Custom Bundle').Layout(layout)

while True:
    event, values = window.Read()

    game_bin = values[0]
    host_bin = values[1]
    bundle_target_dir = values[2]
    bundle_name = values[5]
    bundle_description = values[6]

    progress_meter_chooser_flag = False
    progress_meter_game_flag = False

    deleted_items_list = []
    chooser_deleted_items_list = []

    if event is None or event == 'Exit':
        break

    # add a game found to the game list for later
    if event == add_game_button_label:
        print('Add another game button was pressed')
        if values[4] != '':
            package_list.append(values[4])
            my_tuple = list_to_tuple(package_list)  # convert to format for the UI
            window.FindElement('_LISTBOX_').Update(values=my_tuple)

    # add a chooser found to the chooser list for later
    if event == add_chooser_button_label:
        print('Add another chooser button was pressed')
        if values[3] != '':
            chooser_package_list.append(values[3])
            my_tuple = list_to_tuple(chooser_package_list) # convert to format for the UI
            window.FindElement('_CHOOSER_LISTBOX_').Update(values=my_tuple)

    # remove a chooser item from the list
    if event == delete_chooser_button_label:
        for item in values['_CHOOSER_LISTBOX_']:
            print('listbox item selected for deletion: ', item)
            chooser_deleted_items_list.append(item)
        for list_item in chooser_package_list:
            print('package_list contains: ', list_item)
        updated_list = [x for x in chooser_package_list if x not in chooser_deleted_items_list] # update list with diff
        chooser_package_list = updated_list
        print('**** New package_list ****: ', chooser_package_list)
        print('new list items: ', updated_list)
        window.FindElement('_CHOOSER_LISTBOX_').Update(values=(list_to_tuple(updated_list)))

    # remove a game item from the game list
    if event == delete_game_button_label:
        for item in values['_LISTBOX_']:
            print('listbox item selected for deletion: ', item)
            deleted_items_list.append(item)
        for list_item in package_list:
            print('package_list contains: ', list_item)
        updated_list = [x for x in package_list if x not in deleted_items_list] # update list with the diff
        package_list = updated_list
        print('**** New package_list ****: ', package_list)
        print('new list items: ', updated_list)
        window.FindElement('_LISTBOX_').Update(values=(list_to_tuple(updated_list)))

    if event == 'Submit':
        print('button was pressed')
        verify_paths()

        create_empty_folder(bundle_target_dir)
        empty_dir(bundle_target_dir)

        if chooser_package() and game_package():
            print("Everything's going according to plan.  Making the bundle.")
            call_package(bundle_name, bundle_target_dir, bundle_description) # all this work leads to this moment

            sg.Popup('Bundle successfully created. OK to close app.')

        else:
            print("Requirements to build a package not met, so keep looping.")

window.Close()
