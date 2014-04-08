//var VERSION = "1.1";
var STATE = 1; //states: 1 is waiting for message 3 is waiting for server response
//var TOKEN = "";//verification token is temp stored here
//var ROOM = 0;
var SOCKET;
var serverinfo = '192.168.1.104:600'

$(document).ready(function(){        
    if( typeof(WebSocket) != "function" ) {
       $('cat-page').html("<h1>Error</h1><p>Your browser does not support HTML5 Web Sockets. Try the <a href=\"www.google.com/chrome\">latest Google Chrome</a> instead.</p>");
    }
    log("browser check passed");

    //log("client loaded");
});

//log a notice or error
function log(msg){
        console.log('websockets: ' + msg.toString())
}
//request a refresh of the settings
function loadValues(){
	SOCKET.send("resendValues");
	STATE =1;
}
//log in to the socketserver
function login(username, password, server, port){
    var host = "ws://" + server + ':' + port;
    log("Trying to connect to host: " + host + " ...");
    try
    {
        SOCKET = new WebSocket(host);
        //log('Socket Status: ' + SOCKET.readyState);
        SOCKET.onopen = function(){
            //log('Socket Status: ' + SOCKET.readyState+' (open)');
            log("Connected! trying to login...");
            var logindata = {
                'username': username,
                'password': password,
            }
            var loginpackage = JSON.stringify(logindata);
            SOCKET.send(loginpackage);   
            STATE = 2;
        }
        
        SOCKET.onmessage = function(event){
            msg = event.data;
            log("state: " + STATE + "; message received: " + msg );
            switch(STATE)
            {
            case 1:
                //handle incoming messagesrea
                try{
                    var values = eval('(' + msg + ')');
                    //console.log("received message: " + values);
                    updateValuesJSON(values);
                }catch(exception){
                    log("error parsing incoming JSON: " + exception);
                }
                //not yet made
                break;
            case 2:
                //response from the server to a send message.
                if(msg.substring(0,2) == 'OK'){  //message starts with OK, meaning everything is fine
                    log("server verified sended message");
                }
                else{ //has no OK,
                    //if message has a :, it contains a message back from the server. if not is is invalid
                    msg = msg.split(':');
                    switch(msg[0]){
                        case "E": //error
							alert("Something went wrong in the server: "+msg[1]+"\nNow going back to login");
							window.location = "/login.php?log=uit";
                            //back to loginpage
                        break;
                        case "W": //warning
                            alert("The operation you tried is not permitted, nothing happened.\nReason: ");
                            //do nothing
                        break; 
                        case "R": //response
                            log("The server send a message back: ");
                            //do something with the received data
                        break;
                        default:
                            log("The server send an invalid message back: ");
                        break;
                    }

                }
                STATE = 1;  //back to state 2 to receive normal messages
                break;
            }
        }
        
        SOCKET.onclose = function(){
            log('Socket Status: ' + SOCKET.readyState+' (Closed)');
            //alert('De verbinding met de server is gesloten. Vernieuw de pagina om opnieuw te proberen.')
			if(confirm("De verbinding is verloren, opnieuw proberen?")){
				login(username, password, server, port);
			}
            STATE = 1;
        }
        SOCKET.onerror = function(){
            log('Socket error, status: '+ SOCKET.readyState);
        }
    }catch(exception)
    {
        log("Error occured: " + exception);
    }
}
function updateValuesJSON (values){
	if(builded){
	    for (var key in values){
		    name = key;
		    type = values[key][0];
		    value = values[key][1];
		    log("msg received: set " + name + " ("+ type +") to "+ value);
		    updateValue(name, type, value);
		}
	}else{
		setTimeout(function(){updateValuesJSON(values)},200);
	}
	
}

//post a value asynchronous via doUpdate.php to the database
//only used for users' colors.
function postValue(pvalue, pwhere1, pwhere2, ptable){
 //post changed settings to doUpdate.php that puts the new values in the database
    $.post('doUpdate.php', { value: pvalue, where1: pwhere1, where2: pwhere2, table: ptable })//send post update
    .done(function(data){ //if succesfull post
        if(data) window.alert(data); //usually not enough rights exception. If success, nothing is returned, data=NULL, then nothing is shown.
    })
    .fail(function(data){ //xmlhttprequest failed, server is not available
        window.alert("De server is niet bereikbaar, probeer later opnieuw");
    });

}
