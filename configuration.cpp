#include "configuration.h"
#include "./ui_mainwindow.h"

#include <QMap>
#include <QFile>
#include <QString>
#include <QDir>
#include <QJsonDocument>
#include <QJsonObject>
#include <QProcess>
#include <QFontDatabase>

Configuration::Configuration(Ui::MainWindow *ui, QObject *parent): QObject(parent)
{
    this->ui = ui;
    this->configFiles["bupt"] = new QFile();
    this->configFiles["feishu"] = new QFile();
    setFiles();
    connect(ui->clearConfig_pushButton, &QPushButton::clicked, this, &Configuration::clearConfig);
    connect(ui->reloadConfig_pushButton, &QPushButton::clicked, this, &Configuration::readConfig);
    readConfig();

    this->userChanged = false;
    connect(ui->CAS_userid_lineEdit, &QLineEdit::textEdited, this, [=](){this->userChanged = true;});
    connect(ui->CAS_password_lineEdit, &QLineEdit::textEdited, this, [=](){this->userChanged = true;});
    connect(ui->feishu_appid_lineEdit, &QLineEdit::textEdited, this, [=](){this->userChanged = true;});
    connect(ui->feishu_appsecret_lineEdit, &QLineEdit::textEdited, this, [=](){this->userChanged = true;});
    connect(ui->feishu_admin_comboBox, &QComboBox::currentIndexChanged, this, [=](){this->userChanged = true;});
    connect(ui->feishu_admin_lineEdit, &QLineEdit::textEdited, this, [=](){this->userChanged = true;});
}

Configuration::~Configuration()
{
    for(auto [name, file]: this->configFiles.asKeyValueRange())
    {
        delete file;
    }
}

void Configuration::setFiles()
{
    this->configFiles["bupt"]->setFileName("./BUPT_Crawler/config/bupt.json");
    this->configFiles["feishu"]->setFileName("./BUPT_Crawler/config/feishu.json");
}

void Configuration::clearConfig()
{
    ui->CAS_userid_lineEdit->clear();
    ui->CAS_password_lineEdit->clear();
    ui->feishu_appid_lineEdit->clear();
    ui->feishu_appsecret_lineEdit->clear();
    ui->feishu_admin_lineEdit->clear();
    this->userChanged = true;
}

void Configuration::readConfig()
{
    //Read bupt.json
    if(this->configFiles["bupt"]->open(QIODeviceBase::ReadOnly))
    {
        QJsonObject cas = QJsonDocument::fromJson(this->configFiles["bupt"]->readAll()).object().value("cas").toObject();
        ui->CAS_userid_lineEdit->setText(cas.value("username").toString());
        ui->CAS_password_lineEdit->setText(cas.value("password").toString());
        ui->CAS_password_lineEdit->setCursorPosition(0);
        this->configFiles["bupt"]->close();
    }
    else
    {
        ui->textEdit->append("读取配置bupt.json失败");
        if(this->configFiles["bupt"]->exists())
        {
            ui->textEdit->append("配置文件bupt.json无法打开");
        }
        else if(QFile::copy("./BUPT_Crawler/config/bupt.json.example", "./BUPT_Crawler/config/bupt.json"))
        {
            ui->textEdit->append("配置文件bupt.json不存在");
        }
        else
        {
            ui->textEdit->append("复制配置模板失败");
        }
    }

    //Read feishu.json
    if(this->configFiles["feishu"]->open(QIODeviceBase::ReadOnly))
    {
        QJsonObject feishu = QJsonDocument::fromJson(this->configFiles["feishu"]->readAll()).object();
        ui->feishu_appid_lineEdit->setText(feishu.value("appID").toString());
        ui->feishu_appid_lineEdit->setCursorPosition(0);
        ui->feishu_appsecret_lineEdit->setText(feishu.value("appSecret").toString());
        ui->feishu_appsecret_lineEdit->setCursorPosition(0);

        if(!feishu.value("admin").isObject())
        {
            ui->feishu_admin_comboBox->setCurrentIndex(2);
            ui->feishu_admin_lineEdit->setText(feishu.value("admin").toString());
        }
        else
        {
            QJsonObject admin = feishu.value("admin").toObject();
            if(!admin.value("mobile").isNull())
            {
                ui->feishu_admin_comboBox->setCurrentIndex(0);
                if(admin.value("mobile").isString())
                {
                    ui->feishu_admin_lineEdit->setText(admin.value("mobile").toString());
                }
                else
                {
                    ui->feishu_admin_lineEdit->setText(QString::number(admin.value("mobile").toDouble(), 'f', 0));
                }
            }
            else if(!admin.value("email").isNull())
            {
                ui->feishu_admin_comboBox->setCurrentIndex(1);
                ui->feishu_admin_lineEdit->setText(admin.value("email").toString());
            }
            else
            {
                ui->feishu_admin_comboBox->setCurrentIndex(2);
                if(!admin.value("open_id").isNull())
                {
                    ui->feishu_admin_lineEdit->setText(admin.value("open_id").toString());
                }
            }
        }
        ui->feishu_admin_lineEdit->setCursorPosition(0);
        this->configFiles["feishu"]->close();
    }
    else
    {
        ui->textEdit->append("读取配置feishu.json失败");
        if(this->configFiles["feishu"]->exists())
        {
            ui->textEdit->append("feishu.json无法打开");
        }
        else if(QFile::copy("./BUPT_Crawler/config/feishu.json.example", "./BUPT_Crawler/config/feishu.json"))
        {
            ui->textEdit->append("配置文件feishu.json不存在");
        }
        else
        {
            ui->textEdit->append("复制配置模板失败");
        }
    }
    this->userChanged = false;
}

void Configuration::saveConfig()
{
    if(!this->configFiles["bupt"]->open(QIODeviceBase::WriteOnly) ||
        !this->configFiles["feishu"]->open(QIODeviceBase::WriteOnly))
    {
        emit saveFailed();
        return;
    }
    QJsonObject bupt_cas;
    bupt_cas["username"] = ui->CAS_userid_lineEdit->text();
    bupt_cas["password"] = ui->CAS_password_lineEdit->text();
    QJsonObject bupt_win;
    bupt_win["username"] = bupt_win["password"] = "";
    QJsonObject bupt_root;
    bupt_root["cas"] = bupt_cas;
    bupt_root["win"] = bupt_win;
    QJsonDocument bupt(bupt_root);
    this->configFiles["bupt"]->write(bupt.toJson());
    this->configFiles["bupt"]->close();

    QJsonObject feishu_root;
    feishu_root["appID"] = ui->feishu_appid_lineEdit->text();
    feishu_root["appSecret"] = ui->feishu_appsecret_lineEdit->text();
    QJsonObject feishu_admin;
    ui->feishu_admin_comboBox->currentIndex() == 0? feishu_admin["mobile"] = ui->feishu_admin_lineEdit->text(): feishu_admin["mobile"] = QJsonValue::Null;
    ui->feishu_admin_comboBox->currentIndex() == 1? feishu_admin["email"] = ui->feishu_admin_lineEdit->text(): feishu_admin["email"] = QJsonValue::Null;
    ui->feishu_admin_comboBox->currentIndex() == 2? feishu_admin["open_id"] = ui->feishu_admin_lineEdit->text(): feishu_admin["open_id"] = QJsonValue::Null;
    feishu_root["admin"] = feishu_admin;
    QJsonDocument feishu(feishu_root);
    this->configFiles["feishu"]->write(feishu.toJson());
    this->configFiles["feishu"]->close();

    emit saveSuccess();
}
