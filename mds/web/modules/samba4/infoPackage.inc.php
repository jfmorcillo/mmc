<?php
/**
 * (c) 2014 Zentyal, http://www.zentyal.com
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * Author(s):
 *   Julien Kerihuel <jkerihuel@zentyal.com>
 *   Miguel Julián <mjulian@zentyal.com>
 */

require("modules/samba4/includes/common-xmlrpc.inc.php");

/**
 * module declaration
 */
$module = new Module("samba4");
$module->setVersion("1.0.1");
$module->setRevision('$Rev$');
$module->setDescription(_T("SAMBA4 management"), "samba4");
$module->setAPIVersion("1:0:1");
$module->setPriority(20);

$isProvisioned = isSamba4Provisioned();

$provisionSubmodule = _createSamba4ProvisionSubmodule($isProvisioned);
$module->addSubmod($provisionSubmodule);

$sharesSubmodule = _createSamba4SharesSubmodule($isProvisioned);
$module->addSubmod($sharesSubmodule);

$machinesSubmodule = _createSamba4MachinesSubmodule();
$module->addSubmod($machinesSubmodule);

//    $configurationSubmodule = _createSamba4ConfigurationSubmodule();
//    $module->addSubmod($configurationSubmodule);

$MMCApp =& MMCApp::getInstance();
$MMCApp->addModule($module);


/*
 * Private functions
 */
function _createSamba4ProvisionSubmodule($isProvisioned) {
    $submodule = new SubModule("domaincontroller");

    $submodule->setDescription(_T("Domain", "samba4"));
    $submodule->setImg('modules/samba4/graph/navbar/share');
    $submodule->setDefaultPage("samba4/domaincontroller/provision");
    $submodule->setVisibility(!$isProvisioned);
    $submodule->setPriority(20);

    $provisionPage = new Page("provision",_T("Povisioning", "samba4"));
    $provisionPage->setImg(
        "modules/samba4/graph/img/provision/icn_provision_active.gif",
        "modules/samba4/graph/img/provision/icn_provision.gif"
    );
    $provisionPage->setOptions( array ("visible" => !$isProvisioned));
    $submodule->addPage($provisionPage);

    return $submodule;
}

function _createSamba4SharesSubmodule($isProvisioned) {
    $submodule = new SubModule("shares");

    $submodule->setDescription(_T("Shares-4","samba4"));
    $submodule->setImg('modules/samba4/graph/navbar/share');
    $submodule->setDefaultPage("samba4/shares/index");
    $submodule->setVisibility($isProvisioned);
    $submodule->setPriority(20);

    $listSharesPage = new Page("index",_T("List shares","samba4"));
    $listSharesPage->setImg("modules/samba4/graph/img/shares/icn_global_active.gif",
            "modules/samba4/graph/img/shares/icn_global.gif");
    $listSharesPage->setOptions( array ("visible" => $isProvisioned));
    $submodule->addPage($listSharesPage);

    $addSharePage = new Page("add",_T("Add a share","samba4"));
    $addSharePage->setImg("modules/samba4/graph/img/shares/icn_addShare_active.gif",
            "modules/samba4/graph/img/shares/icn_addShare.gif");
    $addSharePage->setOptions( array ("visible" => $isProvisioned));
    $submodule->addPage($addSharePage);

    $backupPage = new Page("backup",_T("Backup a share","samba4"));
    $backupPage->setOptions( array ("noHeader" => True,"visible" => False));
    $submodule->addPage($backupPage);

    $deleteShare = new Page("delete",_T("Remove a share","samba4"));
    $deleteShare->setOptions( array ("noHeader" => True,"visible" => False));
    $submodule->addPage($deleteShare);

    $shareDetailsPage = new Page("edit",_T("Edit share","samba4"));
    $shareDetailsPage->setOptions( array ("visible" => False));
    $submodule->addPage($shareDetailsPage);

    return $submodule;
}

function _createSamba4MachinesSubmodule() {
    $submodule = new SubModule("machines");
//    $submodule->setVisibility(False);
    $submodule->setImg('modules/base/graph/navbar/computer');
    $submodule->setDefaultPage("samba4/machines/index");
    $submodule->setDescription(_T("Machines"),"samba4");
    $submodule->setPriority(20);
//    $submodule->setAlias('shares');

    $page = new Page("index",_T("Computer list","samba4"));
    $page->setImg("modules/samba4/graph/img/machines/icn_global_active.gif",
                "modules/samba4/graph/img/machines/icn_global.gif");
    $submodule->addPage($page);

    $page = new Page("ajaxFilter");
    $page->setOptions(array("AJAX" =>True,"visible"=>False));
    $submodule->addPage($page);

    $page = new Page("edit",_T("Edit a computer","samba4"));
    $page->setOptions(array("visible"=>False));
    $submodule->addPage($page);

    $page = new Page("delete",_T("Delete a computer","samba4"));
    $page->setOptions( array ("noHeader" => True,"visible"=>False));
    $submodule->addPage($page);

    return $submodule;
}

function _createSamba4ConfigurationSubmodule() {
    $submodule = new SubModule("configuration");

    $submodule->setDefaultPage("samba4/config/index");
    $submodule->setImg('modules/samba4/graph/navbar/pref');
    $submodule->setDescription(_T("Configuration"),"samba4");
    $submodule->setVisibility(False);
    $submodule->setAlias('shares');


    $page = new Page("index",_T("SAMBA configuration","samba4"));
    $page->setImg("modules/samba4/graph/img/config/icn_global_active.gif",
                "modules/samba4/graph/img/config/icn_global.gif");
    $submodule->addPage($page);

    $page = new Page("restart",_T("restart SAMBA service","samba4"));
    $page->setOptions(array("visible"=>False));
    $submodule->addPage($page);

    $page = new Page("reload",_T("Reload SAMBA service","samba4"));
    $page->setOptions(array("visible"=>False));
    $submodule->addPage($page);

    $restoreConfigurationPage = new Page("",_T("Restore SAMBA configuration", "samba4"));
    $restoreConfigurationPage->setOptions(array("visible"=>False));
    $submodule->addPage($restoreConfigurationPage);

    return $submodule;
}

?>
