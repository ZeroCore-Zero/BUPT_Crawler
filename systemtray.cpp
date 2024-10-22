#include "systemtray.h"
#include "./ui_mainwindow.h"

#include <QMenu>

extern QIcon logo;
extern bool mainwindowIsShow;

SystemTray::SystemTray(Ui::MainWindow *ui, QObject *parent): QObject(parent)
{
    this->systemTray = new QSystemTrayIcon(this);
    this->systemTray->setIcon(logo);
    this->systemTray->setToolTip("BUPT_Helper");
    this->systemTray->show();
    connect(this->systemTray, &QSystemTrayIcon::activated, this, [this](QSystemTrayIcon::ActivationReason reason){
        if(reason != QSystemTrayIcon::Trigger || mainwindowIsShow)  return;
        emit needShowMainWindow();
        // this->systemTray->showMessage("显示窗口", "从系统托盘展开窗口", logo, 1000);
    });

    this->trayMenu = new QMenu();
    this->systemTray->setContextMenu(this->trayMenu);
    this->exitAction = new QAction("退出", this->trayMenu);
    this->trayMenu->addAction(this->exitAction);
    connect(this->exitAction, &QAction::triggered, this, [=](){emit quitApp();});
}

SystemTray::~SystemTray()
{
    delete this->systemTray;
    delete this->trayMenu;
    delete this->exitAction;
}
