import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15

ApplicationWindow {
    id: app
    width: collapsedWidth
    height: collapsedHeight
    x: (Screen.width - width) / 2
    y: 10
    visible: true
    title: "AI Agent Dynamic Island"
    color: 'transparent'
    Material.theme: Material.Dark
    Material.accent: Material.Grey
    Material.primary: Material.Dark
    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool

    property bool alarm: false
    property bool screenshot: false
    property bool expanded: false
    property int collapsedWidth: 100
    property int collapsedHeight: 40
    property string lastImageUrl: 'None'

    //island
    property bool listening: false
    property bool thinking: false

    //animation part
    property string property1: 'None'
    property string property2: 'None'
    property int value1: 0
    property int value2: 0
    property int timerValue: 0
    property string alarmValue: 'None'
    property var currentState: states['default']
    property var states: {
        'default' : {
            width: collapsedWidth,
            height: collapsedHeight,
            alarm: false,
            screenshot: false
        },
        'screenshot' : {
            width: 354,
            height: 280,
            interval: 5000,
            alarm: false,
            screenshot: true
        },
        'alarm' : {
            width: 354,
            height: 161,
            interval: 5*1000,
            alarm: true,
            screenshot: false
        }
    }

    function playAnim(property1, value1, property2, value2) {
        var mainRequiredWidth = 0
        var mainRequiredHeight = 0
        if(property1 === "width") {
            mainRequiredWidth = value1
        }
        else if(property2 === "width") {
            mainRequiredWidth = value2
        }

        if(property1 === "height") {
            mainRequiredHeight = value1
        }
        else if(property2 === "height") {
            mainRequiredHeight = value2
        }

        if(main.width === mainRequiredWidth && main.height === mainRequiredHeight) {
            return
        }
        else {
            if(app.width<mainRequiredWidth) app.width = mainRequiredWidth
            if(app.height<mainRequiredHeight) app.height = mainRequiredHeight
            app.property1 = property1
            app.property2 = property2
            app.value1 = value1
            app.value2 = value2
            anim.start()
        }
    }

    SequentialAnimation {
        id: anim
        NumberAnimation {
            target: main
            property: app.property1
            duration: 300
            to: app.value1
            easing.type: Easing.InOutQuad
        }
        NumberAnimation {
            target: main
            property: app.property2
            duration: 300
            to: app.value2
            easing.type: Easing.InOutQuad
        }
        onStopped: {
            if(app.width>main.width) app.width = main.width
            if(app.height>main.height) app.height = main.height
        }
    }

    function getNormalIn(timeS){
        delayedTimer.stop()
        timerValue = timeS
        delayedTimer.start()
    }

    function contentVisibilityReset() {
        app.alarm = currentState.alarm
        app.screenshot = currentState.screenshot
    }

    function mainWindowSizeReset() {
        playAnim('width',currentState.width,'height',currentState.height)
    }

    Timer {
        id: delayedTimer
        interval: app.timerValue
        repeat: false
        onTriggered: {
            app.playAnim('height',collapsedHeight,'width',collapsedWidth)
        }
    }

    Rectangle {
        id: main
        width: app.collapsedWidth
        height: app.collapsedHeight
        radius: 20
        color: "black"
        anchors.horizontalCenter: parent.horizontalCenter
        clip: true

        Rectangle{
            id: face_dummy
            color: 'transparent'
            width: app.collapsedWidth
            height: app.collapsedHeight
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Rectangle {
            color: "transparent"
            height: app.currentState.height-50
            width: app.currentState.width
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: face_dummy.bottom

            Text {
                visible: app.alarm
                text: app.alarmValue
                color: "white"
                anchors.centerIn: parent
                font.pixelSize: 60  
                font.bold: true
                font.family: 'Comic Sans MS'
                //anchors.margins: 10
            }

            Item{
                visible: app.screenshot
                width: parent.width
                height: parent.height
                Image {
                    id: imgine
                    width: 332
                    height: 187
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.topMargin: 10
                }

                Rectangle{
                    height: 32
                    width: 332
                    color: 'transparent'
                    y: imgine.y + imgine.height+10
                    anchors.horizontalCenter: parent.horizontalCenter
                    Rectangle{
                        color: 'transparent'
                        width: parent.width - (32+32+5)
                        height: 32
                        anchors.left: parent.left
                        Text{
                            text: app.lastImageUrl
                            anchors.verticalCenter: parent.verticalCenter
                            elide: Text.ElideRight
                            clip: true
                            width:parent.width-10
                            color: 'white'
                        }
                    }

                    Rectangle{
                        color: 'black'
                        width: 32+32+5
                        height: 32
                        anchors.right: parent.right
                        Image{
                            id: explorer
                            width: 30
                            height: 30
                            source: "assets\\explorer.png"

                            MouseArea{
                                anchors.fill: parent
                                onClicked:{
                                    bridge.revealFile(app.lastImageUrl)
                                }
                            }
                        }
                        Image {
                            id: clipboard
                            width: 32
                            height: 32
                            anchors.right: parent.right
                            source: "assets\\copy.png"

                            MouseArea{
                                anchors.fill: parent
                                onClicked:{
                                    if (bridge.copyImageToClipboard(app.lastImageUrl)) {
                                        ToolTip.show("Copied", 1500)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    Window {
        id: island
        width: app.collapsedWidth
        height: app.collapsedHeight
        x: (Screen.width - width) / 2
        y: app.y
        color: "transparent"
        flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        visible: true

        Rectangle {
            id: face
            anchors.fill: parent
            color: 'black'
            radius:20

            Rectangle {
                id: positive_indecator_face
                anchors.fill: parent
                radius: parent.radius
                border.color: '#1EB5A3'
                border.width:4
                color: 'transparent'
                opacity: 0
            }
            SequentialAnimation {
                id: positive_indecator
                PropertyAnimation { target: positive_indecator_face; property: "opacity"; to: 1; duration: 150 }
                PropertyAnimation { target: positive_indecator_face; property: "opacity"; to: 0; duration: 400 }
                onStopped: {
                    app.listening=false
                    app.thinking=false
                }
            }
            Rectangle{
                anchors.centerIn: parent
                anchors.fill: parent
                scale: 0.7
                color: 'transparent'

                AnimatedImage {
                    id: thinkingGif
                    source: "assets\\think.gif"
                    anchors.centerIn: parent
                    fillMode: Image.PreserveAspectFit
                    width: parent.width
                    height: parent.height
                    visible: app.thinking
                    playing: app.thinking
                }

                AnimatedImage {
                    id: listeningGif
                    source: "assets\\sound.gif"
                    anchors.centerIn: parent
                    fillMode: Image.PreserveAspectFit
                    width: parent.width
                    height: parent.height
                    visible: app.listening
                    playing: app.listening
                }
            }
        }
    }

    Window {
        id: adam
        height: 600
        width: height
        x: (Screen.width-width)/2
        y: (Screen.height-height)/2
        color: 'transparent'
        visible: showWind
        Material.theme: Material.Dark
        Material.accent: Material.Gray
        Material.primary: Material.Dark
        flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        property bool turnedOn: false
        property bool showWind: true
        property var camera_devices: []
        property var audio_devices: []
        property int camera_device_index: -1
        property int audio_device_index: -1
        property bool camera_running: false
        property bool mic_running: false

        function showSettings() {
            devices.visible=true
        }

        SequentialAnimation {
            id: anim1
            NumberAnimation {
                target: settings
                property: 'rotation'
                duration: 300
                to: settings.rotation + 60
                easing.type: Easing.InOutQuad
            }
        }
        
        Rectangle {
            anchors.centerIn: parent
            color: "black"
            rotation: 45
            width: Math.sqrt(Math.pow(parent.height, 2) * 0.5)
            height: width

            AnimatedImage {
                id: waveEffect
                source: "assets/listening.gif"
                rotation: 90
                width: parent.width
                height: parent.height
                anchors.centerIn: micIcon
                playing: adam.turnedOn
                visible: false
                smooth: true
                fillMode: Image.PreserveAspectFit
                cache: true
            }

            Image {
                id: micIcon
                height: 80
                rotation: -45
                fillMode: Image.PreserveAspectFit
                source: adam.turnedOn ? "assets/on.png" : "assets/off.png"
                anchors.centerIn: parent
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        adam.turnedOn = !adam.turnedOn;
                        waveEffect.visible = adam.turnedOn;
                        if (adam.turnedOn) bridge.on(true)
                        else bridge.on(false)
                    }
                    onPressAndHold: {
                        if (!adam.turnedOn) Qt.quit()
                    }
                }
            }

            Image{
                id: settings
                width: 32
                height: 32
                fillMode: Image.PreserveAspectFit
                rotation: -45
                source: 'assets/settings.png'
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.rightMargin: 10
                anchors.bottomMargin: 10

                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        if (adam.mic_running || adam.camera_running) {
                            ToolTip.show("Turn off mic and camera related services!", 1500)
                            return
                        }
                        anim1.start()
                        bridge.request_for_devices()
                    }
                }
            }

            Rectangle{
                anchors.fill: parent
                color: 'transparent'
                visible: devices.visible
                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        devices.visible = false
                    }
                }
            }

            Rectangle {
                id: devices
                width: 300
                height: 210
                color: "#1e1e1e" 
                radius: 10
                border.color: "#444"
                border.width: 1
                anchors.centerIn: parent
                visible: false
                rotation: -45

                Column {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 15

                    RowLayout {
                        width: parent.width
                        spacing: 6
                        Rectangle {
                            width: 24
                            height: 24
                            color: 'transparent'
                            Image{
                                anchors.fill: parent
                                fillMode: Image.PreserveAspectFit
                                source: 'assets/camera.png'
                            }
                        }
                        ComboBox {
                            id: camera
                            Layout.fillWidth: true
                            model: adam.camera_devices
                            visible: adam.camera_devices.length>0
                            currentIndex: adam.camera_device_index
                        }
                        Text {
                            text: 'No device found!'
                            visible: adam.camera_devices.length==0
                            color: 'white'
                        }
                    }

                    RowLayout {
                        width: parent.width
                        spacing: 6
                        Rectangle {
                            width: 24
                            height: 24
                            color: 'transparent'
                            Image{
                                anchors.fill: parent
                                fillMode: Image.PreserveAspectFit
                                source: 'assets/mic.png'
                            }
                        }
                        ComboBox {
                            id: audio
                            Layout.fillWidth: true
                            model: adam.audio_devices
                            visible: adam.audio_devices.length>0
                            currentIndex: adam.audio_device_index
                            //Material.theme: Material.Dark
                        }
                        Text {
                            text: 'No device found!'
                            visible: adam.audio_devices.length==0
                            color: 'white'
                        }
                    }

                    Button {
                        text: "OK"
                        anchors.right: parent.right
                        background: Rectangle {
                            color: "#3a3a3a"
                            radius: 5
                        }
                        contentItem: Text {
                            text: "OK"
                            color: "white"
                            font.bold: true
                            anchors.centerIn: parent
                        }
                        onClicked: {
                            bridge.selected_devices(audio.currentIndex,camera.currentIndex)
                            devices.visible = false
                        }
                    }
                }
            }
        }
    }

//Using temporary as a replacement of voice
    Window {
        width: 600
        height: 200
        x: 0
        visible: false
        id: buttons
        RowLayout{
            id: testtube_btr1
            anchors.centerIn: parent
            Button{
                text: "Screenshot"
                onClicked: bridge.takeScreenshotAndSend()
            }
            Button{
                text: "time"
                onClicked: bridge.kk()
            }
            Button{
                text: "Show"
                onClicked: bridge.showapp(true)
            }

            Button{
                text: 'Hide'
                onClicked: bridge.showapp(false)
            }
        }

        RowLayout{
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: testtube_btr1.top
            Button{
                text: 'Start listening'
                onClicked: bridge.isResult(1)
            }

            Button{
                text: 'Start thinking'
                onClicked: bridge.isResult(2)
            }

            Button{
                text: 'Gotcha'
                onClicked: bridge.isResult(3)
            }
            Button{
                text: 'not a recognized as command'
                onClicked: bridge.isResult(4)
            }
        }
        RowLayout{
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: testtube_btr1.bottom
            TextField{
                id: commandField
                width: 400
            }
            Button{
                text: 'Command'
                onClicked: bridge.newCommand(commandField.text)
            }
        }
    }

    Connections {
        target: bridge
        function onScreenshotData(ss, location) {
            app.lastImageUrl = location
            imgine.source = "data:image/png;base64," + ss
        
            app.currentState = states['screenshot']
            contentVisibilityReset()
            playAnim('width',currentState.width,'height',currentState.height)
            getNormalIn(currentState.interval)
        }
        
        function onAlarmData(t) {
            app.alarmValue = t

            app.currentState = states['alarm']
            contentVisibilityReset()
            playAnim('width',currentState.width,'height',currentState.height)
            getNormalIn(currentState.interval)
        }

        function onShowApp(x) {
            adam.showWind = x
        }

        function onCameraOn(x) {
            adam.camera_running = x
        }

        function onMicOn(x) {
            adam.mic_running = x
        }

        function onAvailableDevices(audio,i, camera, j){
            adam.camera_devices = camera
            adam.audio_devices = audio
            adam.audio_device_index = i
            adam.camera_device_index = j
            adam.showSettings()
        }

        function onListening(x) {
            app.listening = x
            //app.thinking = false
        }
        
        function onThinking() {
            app.thinking = true
            app.listening = false
        }

        function onGotResult(xbool) {
            if(xbool===true) positive_indecator.restart()
            else {
                app.listening = false
                app.thinking = false
            }
        }
    }
}