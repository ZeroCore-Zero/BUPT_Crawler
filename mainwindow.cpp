#include "mainwindow.h"
#include "./ui_mainwindow.h"
#include <QFile>
#include <QFileDialog>
#include <QString>
#include <QDir>
#include <QProcess>
#include <QFontDatabase>
#include <QIcon>
#include <QSystemTrayIcon>
#include <QMenu>
#include <QMessageBox>
#include <QCloseEvent>

extern QIcon logo;
bool mainwindowIsShow;

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    setWindowIcon(logo);
    mainwindowIsShow = true;
    QDir::setCurrent(qApp->applicationDirPath());

    // Crawler
    this->crawler = new Crawler(ui, this);
    this->crawler->sem = &this->sem;
    if(!QDir("./BUPT_Crawler").exists())
    {
        ui->textEdit->append("爬虫文件夹不存在");
        this->disableLayoutWidgets(ui->manageLayout);
        this->crawler->statues = Crawler::Statues::DISABLE;
    }

    // Configuration
    this->configuration = new Configuration(ui, this);
    this->configuration->sem = &this->sem;
    this->crawler->configurationChanged = &this->configuration->userChanged;
    connect(this->crawler, &Crawler::needSaveConfig, this->configuration, &Configuration::saveConfig);
    connect(this->configuration, &Configuration::saveFailed, this->crawler, [=](){this->crawler->configurationSaved = false; this->sem.release();});
    connect(this->configuration, &Configuration::saveSuccess, this->crawler, [=](){this->crawler->configurationSaved = true; this->sem.release();});

    // SystemTray
    this->systemTray = new SystemTray(ui, this);
    connect(ui->hideWindow, &QAction::triggered, this, [this](){
        this->hide();
        mainwindowIsShow = false;
        // this->systemTray->showMessage("隐藏窗口", "窗口隐藏到系统托盘", logo, 1000);
    });
    connect(this->systemTray, &SystemTray::needShowMainWindow, this, [this](){this->show(); mainwindowIsShow = true;});
    connect(this->crawler, &Crawler::Stoped, this, [this](){
        if(!mainwindowIsShow)   this->systemTray->showMessage("进程停止", "进程由于意外停止", logo);
    });
    connect(this->systemTray, &SystemTray::quitApp, this, [this](){this->close();});

    // Fonts
    int fontID = QFontDatabase::addApplicationFont(":/fonts/HarmonyOS_Sans_Black.ttf");
    QStringList fontFamilies = QFontDatabase::applicationFontFamilies(fontID);
    fontFamilies.append("Microsoft YaHei");
    QFont font(fontFamilies);
    this->setFont(font);

    //Menus
    connect(ui->actionClearTextEdit, &QAction::triggered, this, [=](){ui->textEdit->clear();});
    connect(ui->actionChangeCWD, &QAction::triggered, this, &MainWindow::changeCWD);
}

MainWindow::~MainWindow()
{
    delete this->crawler;
    delete this->configuration;
    delete this->systemTray;
    delete ui;
}

void MainWindow::closeEvent(QCloseEvent *event)
{
    if(this->crawler->statues != Crawler::Statues::RUN)
    {
        event->accept();
        return;
    }
    QMessageBox::StandardButton result
        = QMessageBox::question(this, "退出", "确定退出吗？",
                               QMessageBox::Yes|QMessageBox::No,
                               QMessageBox::No);

    if (result == QMessageBox::Yes) event->accept();
    else    event->ignore();
}

void MainWindow::keyPressEvent(QKeyEvent *event)
{
    if((event->key() == Qt::Key_Enter || event->key() == Qt::Key_Return) &&
        this->crawler->statues == Crawler::Statues::STOP)
        this->crawler->RSCrawler();
}

void MainWindow::disableLayoutWidgets(QLayout *layout) {
    if (!layout) return;

    QLayoutItem *item = layout->itemAt(0);
    while (item) {
        if (item->widget()) {
            item->widget()->setEnabled(false);
            item->widget()->setStyleSheet("color: gray; background-color: lightgray;");
        } else if (item->layout()) {
            disableLayoutWidgets(item->layout());
        }
        item = layout->itemAt(layout->indexOf(item) + 1);
    }
}

void MainWindow::enableLayoutWidgets(QLayout *layout) {
    if (!layout) return;

    QLayoutItem *item = layout->itemAt(0);
    while (item) {
        if (item->widget()) {
            item->widget()->setEnabled(true);
            item->widget()->setStyleSheet("");
        } else if (item->layout()) {
            enableLayoutWidgets(item->layout());
        }
        item = layout->itemAt(layout->indexOf(item) + 1);
    }
}

void MainWindow::changeCWD()
{
    QString dirPath = QFileDialog::getExistingDirectory(this, "选择目录", QDir::homePath());
    if(dirPath.isEmpty())   return;
    if(!QDir::setCurrent(dirPath))
    {
        ui->textEdit->append("目录切换失败。");
        return;
    }
    emit CWDChanged();
    qDebug() << "New CWD:" << QDir::currentPath();
    QMessageBox::information(this, "成功", "目录切换成功。");
    ui->textEdit->append("目录切换成功。");
    if(!QDir("./BUPT_Crawler").exists())
    {
        ui->textEdit->append("爬虫文件夹不存在");
        this->disableLayoutWidgets(ui->manageLayout);
        this->crawler->statues = Crawler::Statues::DISABLE;
    }
    else
    {
        enableLayoutWidgets(ui->manageLayout);
        this->configuration->setFiles();
        this->configuration->readConfig();
        this->crawler->statues = Crawler::Statues::STOP;
    }
}
