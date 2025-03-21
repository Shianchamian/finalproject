"""
This file defines screens for the face recognition app using KivyMD. 
It shows how to create different screens for user info, face registration, and recognition, 
along with navigation using a bottom navigation bar and a navigation drawer. 
"""

screen_helper = """
ScreenManager:
    LoginScreen:

    MainScreen:
    UserScreen:
    HistoryScreen:

    FaceInfoScreen:
    AddFaceScreen:
    SuccessScreen:

    RecognitionScreen:
    ResultScreen:


    FacesScreen: 
    TransferScreen:

<LoginScreen>:
    name: "login"
    AnchorLayout:
        anchor_x: "center"
        anchor_y: "center"

        BoxLayout:
            orientation: "vertical"
            size_hint: (None, None)
            width: dp(300)
            height: dp(200)
            spacing: dp(10)

            MDTextField:
                id: password_input
                password: True
                hint_text: "Password(1234)"
                left_icon: "key"
                size_hint_x: 1 
                height: dp(48)

            MDRaisedButton:
                text: "Login"
                size_hint_x: 1
                height: dp(48)
                on_release: app.check_login(password_input.text)


<MainScreen>:
    name: 'main'
    MDNavigationLayout:
        ScreenManager:
            Screen:
                BoxLayout:
                    orientation: 'vertical'

                    MDTopAppBar:
                        title: 'Face Recognition App'
                        right_action_items: [["clock", lambda x:  app.see_history()]] 
                        left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]
                        elevation: 1
                        
                        # widget:

                    BoxLayout:
                        id: content_area  
                        size_hint_y: 0.8
                        orientation: 'vertical'
                        padding: dp(20) 
                        spacing: dp(20)  
                        
                        # MDLabel:
                        #     text: "Welcome!"
                        #     halign: "center"
                        #     font_style: "H5"
                        #     theme_text_color: "Primary"

                    MDBottomNavigation:
                        size_hint_y: 0.2

                        MDBottomNavigationItem:
                            name: 'home'
                            icon: 'home'
                            text: 'Homepage'
                            on_tab_press: app.go_home()

                        MDBottomNavigationItem:
                            name: 'recognize'
                            icon: 'face-recognition'
                            text: 'Recognition'
                            on_tab_press: app.recognize_face()
                        
                        MDBottomNavigationItem:
                            name: 'add'
                            icon: 'plus'
                            text: 'Add'
                            on_tab_press: app.add_face()

        MDNavigationDrawer:
            id: nav_drawer 
            orientation: 'vertical'
            padding: dp(15)
            spacing: dp(10)
            
            MDLabel:
                id: user_name_label
                text: "Welcome, User"
                font_style: "H6"
                theme_text_color: "Secondary"
                height: self.texture_size[1] + dp(10)
            
           
            ScrollView:
                MDList:
                    OneLineIconListItem:
                        text: 'User Information'
                        on_release: app.sm.current = "user"
                        IconLeftWidget:
                            icon: 'account'


                    # OneLineIconListItem:
                    #     text: 'How to use'
                    #     IconLeftWidget:
                    #         icon: 'help'

                    OneLineIconListItem:
                        text: 'Manage faces'
                        on_release: app.manage_face()
                        IconLeftWidget:
                            icon: 'database'

                    # OneLineIconListItem:
                    #     text: 'Data transfer'
                    #     # on_release: app.root.current = "transfer"
                    #     IconLeftWidget:
                    #         icon: 'cellphone'

                    OneLineIconListItem:
                        text: 'Dark Mode'
                        IconLeftWidget:
                            icon: 'weather-night'

                        MDSwitch:
                            id: dark_mode_switch
                            pos_hint: {"center_x": 0.8}
                            on_active: app.toggle_theme(self.active)

<HistoryScreen>:
    name: 'history'
    BoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: "History"
            left_action_items: [["arrow-left", lambda x: app.go_home()]]
            right_action_items: [["delete-forever", lambda x: app.clear_history()]]

            elevation: 1

        ScrollView:
            MDList:
                id: history_list
                    

<FaceInfoScreen>:
    name: "face_info"

    BoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Register Face Information"
            left_action_items: [["arrow-left", lambda x: app.go_home()]]
            # elevation: 1
        
        BoxLayout:
            orientation: "vertical"
            padding: dp(20)
            spacing: dp(20)

            MDLabel:
                text: "Register Face Information"
                halign: "center"
                font_style: "H5"

            MDTextField:
                id: name_input
                hint_text: "Enter Name"
                helper_text: "Name of the person"
                helper_text_mode: "on_focus"

            MDTextField:
                id: relation_input
                hint_text: "Enter Relation"
                helper_text: "Relation (e.g., Friend, Family...)"
                helper_text_mode: "on_focus"

            MDRaisedButton:
                text: "Continue"
                pos_hint: {"center_x": 0.5}
                on_release: app.go_to_add_face()

<AddFaceScreen>:
    name: 'add'
    BoxLayout:
        padding: dp(20)
        spacing: dp(20)
        orientation: 'vertical'

        MDIconButton:
            icon: 'arrow-left'
            on_release:  app.go_back()

        # MDIconButton:
        #     icon: 'camera-party-mode'
        #     on_release:  app.switch_camera()

        Image:
            id: camera_feed
            allow_stretch: True
            keep_ratio: True 
            size_hint: 1, 1 

        MDLabel:
            id: label
            text: "Face not visible.Please move closer to the camera"
            font_size: "20sp"
            halign: "center"
            pos_hint: {"center_x": 0.5, "center_y": 0.5}

        MDProgressBar:
            id: progress_bar
            value: 0  
            size_hint_x: 0.6
            size_hint_y: None
            height: dp(10)
            pos_hint: {"center_x": 0.5}

<SuccessScreen>:
    name: "success"

    BoxLayout:
        orientation: "vertical"
        spacing: dp(50)
        padding: dp(50)  
        size_hint: None, None
        size: dp(500), dp(600) 
        pos_hint: {"center_x": 0.5, "center_y": 0.5}

        Widget:
            size_hint_y: None
            height: dp(50)

        MDIcon:
            icon: "check-circle"
            size_hint: None, None
            size: dp(120), dp(120)
            theme_text_color: "Custom"
            font_size: dp(100)
            text_color: 0, 0.6, 0.6, 1
            pos_hint: {"center_x": 0.5}

        MDLabel:
            text: "Face Added!"
            halign: "center"
            font_style: "H4"
            size_hint_y: None
            height: dp(50)

        Widget:
            size_hint_y: None
            height: dp(50)

        MDFillRoundFlatIconButton:
            text: "Continue"
            icon: "arrow-right"
            icon_pos: "right"
            size_hint: None, None
            size: dp(200), dp(50)
            pos_hint: {"center_x": 0.5}
            on_release: app.go_home()
            

<RecognitionScreen>:
    name: 'recognize'
    BoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: "Face Recognition"
            left_action_items: [["arrow-left", lambda x: app.go_home()]]
            right_action_items: [["camera-party-mode", lambda x: app.switch_camera()]]
            elevation: 1

        Image:
            id: camera_feed
            allow_stretch: True
            keep_ratio: True 
            size_hint: 1, 1 
        
        MDLabel:
            id: recognition_label
            text: "Waiting for recognition..."
            font_size: "20sp"
            halign: "center"
            pos_hint: {"center_x": 0.5, "center_y": 0.5}

        MDIconButton:
            icon: "camera"
            pos_hint: {"center_x": 0.5,"center_y": 0.2} 
            on_release: app.sm.get_screen("recognize").open_result_screen()
            
<ResultScreen>:
    name: "result"
    BoxLayout:
        orientation: "vertical"
        padding: dp(20)
        spacing: dp(20)

        Image:
            id: result_image
            allow_stretch: True
            font_size: dp(100)
            size_hint: 1, 0.6
        
        MDIcon:
            id: result_icon
            icon: "check-circle"
            size_hint: None, None
            size: dp(120), dp(120)
            theme_text_color: "Custom"
            font_size: dp(100)
            text_color: 0, 0.6, 0.6, 1  # **Teal 色**
            pos_hint: {"center_x": 0.5}

        MDLabel:
            id: result_label
            text: "Processing..."
            halign: "center"
            font_style: "H5"
            theme_text_color: "Primary"

        MDFillRoundFlatIconButton:
            text: "Return"
            icon: "arrow-left"
            pos_hint: {"center_x": 0.5}
            on_release: app.go_home()



<FacesScreen>:
    name: 'db'
    BoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: "Manage Faces"
            left_action_items: [["arrow-left", lambda x: app.go_home()]]
            elevation: 1

        ScrollView:
            MDList:
                id: faces_list

<TransferScreen>:
    name: 'transfer'
    BoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Data Transfer"
            left_action_items: [["arrow-left", lambda x: app.go_back()]]
            # elevation: 1

        MDLabel:
            text: "Data Transfer"
            halign: "center"
            font_style: "H5"

        MDRaisedButton:
            text: "Export Database"
            icon: "upload"
            pos_hint: {"center_x": 0.5}
            # on_release: app.export_database()

        MDRaisedButton:
            text: "Import Database"
            icon: "download"
            pos_hint: {"center_x": 0.5}
            # on_release: app.import_database()

<UserScreen>:
    name: "user"

    BoxLayout:
        orientation: "vertical"
        spacing: dp(20)
        padding: dp(20)

        MDLabel:
            text: "User Information"
            halign: "center"
            font_style: "H5"

        MDTextField:
            id: name_input
            hint_text: "Enter your name"
            helper_text: "Your full name"
            helper_text_mode: "on_focus"

        MDTextField:
            id: address_input
            hint_text: "Enter your address"
            helper_text: "Your home address"
            helper_text_mode: "on_focus"

        MDTextField:
            id: contact_input
            hint_text: "Enter emergency contact"
            helper_text: "Phone number of emergency contact"
            helper_text_mode: "on_focus"
            input_filter: "int"

        MDRaisedButton:
            text: "Save Information"
            pos_hint: {"center_x": 0.5}
            on_release: app.save_user_info(name_input.text, address_input.text, contact_input.text)

        MDRaisedButton:
            text: "Back to Home"
            pos_hint: {"center_x": 0.5}
            on_release: app.root.current = "main"
        
"""
