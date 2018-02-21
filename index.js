const electron = require('electron');
const { app, BrowserWindow, ipcMain, Menu } = electron;
const moment = require('moment-timezone');
const sqlite3 = require('sqlite3').verbose();
const dedupe = require('dedupe');
const oui = require('oui');
const exists = require('fs-exists-sync');
const { exec, execFile } = require('child_process');

const sqlite_file = "./api/iotinsight.db";
const db = new sqlite3.Database(sqlite_file);

let MainWindow;
let subFlask;
let subRedis;
let subCelery;

app.on('window-all-closed', function() {
	app.quit();
});

app.on('quit', function() {
	subFlask.kill('SIGHUP');
	subRedis.kill('SIGHUP');
	subCelery.kill('SIGHUP');
});

global.sharedObj = {
	timezone : 'Asia/Seoul'
};

app.on('ready', () => {

	subFlask = exec('cd api && python app.py', (error, stdout, stderr) => {});

	subRedis = execFile('api\\bin\\redis-server.exe', (error, stdout, stderr) => {});

	subCelery = exec('cd api && celery -A tasks worker --loglevel=info -P eventlet', (error, stdout, stderr) => {});

	MainWindow  = new BrowserWindow({
		width : 1280,
		height : 720
	});

	MainWindow.loadURL('file://' + __dirname + '/pages/getInfoPage.html');
	MainWindow.on('close', () => app.quit() );

	const menu = Menu.buildFromTemplate(template)
	Menu.setApplicationMenu(menu)


	MainWindow.on('closed', function() {
		MainWindow = null;
	})
});

// get timezone
ipcMain.on('get-timezone', function(event) {

});

// start parsing Database
ipcMain.on('start-parsing', function(event) {

	makeNetworkMap();

	getAlHistorys();
	getAlSettings();

	getSamDeviceData();
	getSamEventsData();
	getSamHubsData();
	getSamLocationsData();

	getOnCommands_command ();
	getOnStationsData();
	getOnSettingsData();

});

// ----------------------------------------------------------------------------------------- //
// ----------------------------- Make Network Map ------------------------------------------ //
// ----------------------------------------------------------------------------------------- //

// networkMap variable
const network_data = {};
network_data['nodes'] = [];
network_data['edges'] = [];



// Send networkMap Data to html
ipcMain.on('networkMap-get', (event, arg) => {
    event.sender.send('networkMap-get-reply', network_data);
});

function makeNetworkMap() {

	const macAddrList = [];

	db.all("SELECT DISTINCT dst_macaddr, src_macaddr FROM packets", function(err, rows) {
		for (var index = 0; index < rows.length; index++) {
			macAddrList.push(rows[index].dst_macaddr.toString(16).match( /.{1,2}/g ).join( ':' ), rows[index].src_macaddr.toString(16).match( /.{1,2}/g ).join( ':' ));
		}

		const macAddrListDedupe = dedupe(macAddrList);

		for (var index = 0, len = macAddrListDedupe.length; index < len; index++) {
			try {
				// Insert the icon if the vendor exists.
				if(!exists(vendor = './dist/img/' +  oui(macAddrListDedupe[index]).split('\n')[0] + '.png')) {
					var data = {
						id: index + 1,
						label: macAddrListDedupe[index]
					};
				}
				else {
					var data = {
						id: index + 1,
						label: macAddrListDedupe[index],
						image: '.' + vendor,
						shape: 'image'
					};
				}
				network_data['nodes'].push(data);
			}
			catch (exception) {
				console.log(exception);
			}
		}

		for (var index = 0, len = macAddrListDedupe.length; index < len; index++) {
			try {
				// Insert the icon if the vendor exists.
				var edgesData = {
					from : macAddrListDedupe.indexOf(rows[index].src_macaddr.toString(16).match( /.{1,2}/g ).join( ':' )) + 1,
					to : macAddrListDedupe.indexOf(rows[index].dst_macaddr.toString(16).match( /.{1,2}/g ).join( ':' )) + 1,
					arrows :'to',
					length : 300
				};
			network_data['edges'].push(edgesData);
			}
			catch (exception) {
				console.log(exception);
			}
		}
	});
}

// ----------------------------------------------------------------------------------------- //
// ----------------------------- Make Alexa Data ------------------------------------------- //
// ----------------------------------------------------------------------------------------- //

var alHistorysData = [];
var alSettingsData = [];

// Send onHub-stations Data to html
ipcMain.on('alexa-history-data-get', (event, arg) => {
    event.sender.send('alexa-history-data-get-reply', alHistorysData);
});

function getAlHistorys() {
	db.all("SELECT * FROM al_historys", function(err, rows) {
		for (var index = 0; index < rows.length; index++) {
			alHistorysData.push([
				rows[index]._id, 
				rows[index].activity_name, 
				moment.tz(rows[index].activity_time, "UTC").clone().tz(global.sharedObj.timezone).format(), 
				rows[index].status, 
				rows[index].command, 
				rows[index].audio_link
			]);
		}
	});
}

ipcMain.on('alexa-settings-data-get', (event, arg) => {
    event.sender.send('alexa-settings-data-get-reply', alSettingsData);
});

function getAlSettings() {
	db.all("SELECT * FROM al_settings", function(err, rows) {
		for (var index = 0; index < rows.length; index++) {
			alSettingsData.push([
				rows[index]._id, 
				rows[index].key, 
				rows[index].value
			]);
		}
	});
}

// Called when retrieving the command from the table, Because the output value is long
ipcMain.on('history-response-get', (event, arg) => {
	getAlHistory_response (arg);
});

function getAlHistory_response (indexNum) {
	db.all("SELECT response FROM al_historys WHERE _id = " + indexNum, function(err, rows) {
		MainWindow.webContents.send('history-response-get-reply', rows);
	});
}

// ----------------------------------------------------------------------------------------- //
// ----------------------------- Make SmartThings Data ------------------------------------- //
// ----------------------------------------------------------------------------------------- //

var samDevicesData = [];
var samEventsData = [];
var samHubsData = [];
var samLocationsData = [];

// Send onHub-stations Data to html
ipcMain.on('smartthings-device-data-get', (event, arg) => {
    event.sender.send('smartthings-device-data-get-reply', samDevicesData);
});

function getSamDeviceData() {
	db.all("SELECT * FROM sam_devices", function(err, rows) {
		for (var index = 0; index < rows.length; index++) {
			samDevicesData.push([
				rows[index]._id, 
				rows[index].name, 
				rows[index].label, 
				rows[index].device_id, 
				rows[index].hub_id, 
				rows[index].device_type, 
				moment.tz(rows[index].create_date, "UTC").clone().tz(global.sharedObj.timezone).format(), 
				moment.tz(rows[index].last_update, "UTC").clone().tz(global.sharedObj.timezone).format(), 
				rows[index].version, 
				rows[index].zigbee_id, 
				rows[index].network_id
			]);
		}
	});
}

// Send onHub-stations Data to html
ipcMain.on('smartthings-event-data-get', (event, arg) => {
    event.sender.send('smartthings-event-data-get-reply', samEventsData);
});

function getSamEventsData() {
	db.all("SELECT * FROM sam_events", function(err, rows) {
		for (var index = 0; index < rows.length; index++) {
			samEventsData.push([
				rows[index]._id, 
				moment.tz(rows[index].event_time, "UTC").clone().tz(global.sharedObj.timezone).format(), 
				rows[index].location_id,
				rows[index].hub_id,
				rows[index].device_id,
				rows[index].event_type,
				rows[index].value,
				rows[index].displayed_text
			]);
		}
	});
}

// Send onHub-stations Data to html
ipcMain.on('smartthings-hubs-data-get', (event, arg) => {
    event.sender.send('smartthings-hubs-data-get-reply', samHubsData);
});

function getSamHubsData() {
	db.all("SELECT * FROM sam_hubs", function(err, rows) {
		for (var index = 0; index < rows.length; index++) {
			samHubsData.push([
				rows[index]._id, 
				rows[index].name, 
				rows[index].hub_id, 
				rows[index].location_id, 
				moment.tz(rows[index].last_serverping, "UTC").clone().tz(global.sharedObj.timezone).format(), 
				moment.tz(rows[index].last_hubping, "UTC").clone().tz(global.sharedObj.timezone).format(), 
				moment.tz(rows[index].create_date, "UTC").clone().tz(global.sharedObj.timezone).format(),
				moment.tz(rows[index].last_update, "UTC").clone().tz(global.sharedObj.timezone).format(), 
				moment.tz(rows[index].last_booted, "UTC").clone().tz(global.sharedObj.timezone).format(),
				rows[index].ip_address, 
				rows[index].mac_address.toString(16).match( /.{1,2}/g ).join( ':' )
			]);
		}
	});
}

// Send onHub-stations Data to html
ipcMain.on('smartthings-location-data-get', (event, arg) => {
    event.sender.send('smartthings-location-data-get-reply', samLocationsData);
});

function getSamLocationsData() {
	db.all("SELECT * FROM sam_locations", function(err, rows) {
		for (var index = 0; index < rows.length; index++) {
			samLocationsData.push([
				rows[index]._id, 
				rows[index].location_id,
				rows[index].name,
				rows[index].temperature_scale,
				rows[index].timezone,
				rows[index].coordinates
			]);
		}
	});
}

// ----------------------------------------------------------------------------------------- //
// ----------------------------- Make OnHub Data ------------------------------------------- //
// ----------------------------------------------------------------------------------------- //

// onHub data variable
var onSettingsData = [];
var onStationsData = [];
var onCommands_command = [];

// Send onHub-commands Data to html
ipcMain.on('onHub-commands-data-get', (event, arg) => {
    event.sender.send('onHub-commands-data-get-reply', onCommands_command);
});

function getOnCommands_command () {
	db.all("SELECT _id, command FROM on_commands", function(err, rows) {
		for (var index = 0; index < rows.length; index++) {
			onCommands_command.push([
				rows[index]._id,
				rows[index].command
			]);
		}
	});
}

// Called when retrieving the command from the table, Because the output value is long
ipcMain.on('commands-output-get', (event, arg) => {
	getOnCommands_output (arg);
});

function getOnCommands_output (indexNum) {
	db.all("SELECT output FROM on_commands WHERE _id = " + indexNum, function(err, rows) {
		MainWindow.webContents.send('commands-output-get-reply', rows);
	});
}

// Send onHub-stations Data to html
ipcMain.on('onHub-stations-data-get', (event, arg) => {
    event.sender.send('onHub-stations-data-get-reply', onStationsData);
});

function getOnStationsData() {
	db.all("SELECT * FROM on_stations", function(err, rows) {
		for (var index = 0; index < rows.length; index++) {
			onStationsData.push([
				rows[index]._id, 
				rows[index].hostname, 
				rows[index].device_id, 
				moment.tz(rows[index].lastseen_time, "UTC").clone().tz(global.sharedObj.timezone).format(), 
				rows[index].is_connected, 
				rows[index].is_guest, 
				rows[index].ip_address, 
				rows[index].mac_address.toString(16).match( /.{1,2}/g ).join( ':' )
			]);
		}
	});
}

// Send onHub-settings Data to html
ipcMain.on('onHub-settings-data-get', (event, arg) => {
    event.sender.send('onHub-settings-data-get-reply', onSettingsData);
});

function getOnSettingsData() {
	db.all("SELECT _id, key, value FROM on_settings", function(err, rows) {
		for (var index = 0; index < rows.length; index++) { 
			if(rows[index].key == 'generateTime') {
				onSettingsData.push([
					rows[index]._id, 
					rows[index].key, 
					moment(rows[index].value * 1000).tz(global.sharedObj.timezone).format()
				]);
			}
			else {
				onSettingsData.push([
					rows[index]._id, 
					rows[index].key, 
					rows[index].value
				]);
			}
		}
	});
}

// ----------------------------------------------------------------------------------------- //
// ----------------------------- electron Options ------------------------------------------ //
// ----------------------------------------------------------------------------------------- //

const template = []
  