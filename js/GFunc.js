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

    log("client loaded");
});

//log a notice or error
function log(msg){
        console.log('websockets: ' + msg.toString())
}

//log in to the socketserver
function login(username, password, server, port){
    var host = "ws://" + server + ':' + port;
    log("Trying to connect to host: " + host + " ...");
    try
    {
        SOCKET = new WebSocket(host);
        log('Socket Status: ' + SOCKET.readyState);
        SOCKET.onopen = function(){
            log('Socket Status: ' + SOCKET.readyState+' (open)');
            log("Connected! trying to login...");
            var logindata = {
                'username': username,
                'password': password,
            }
            var loginpackage = JSON.stringify(logindata)
            SOCKET.send(loginpackage);   
            STATE = 2;
        }
        
        SOCKET.onmessage = function(event){
            msg = event.data;
            //log("state: " + STATE + "; message received: " + msg )
            switch(STATE)
            {
            case 1:
                //handle incoming messagesrea
                try{
                    var values = eval('(' + msg + ')');
                }catch(exception){
                    log("error parsing incoming JSON: " + exception);
                }
                log("received: " + msg);
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
                        case "ERROR":
                            exp = "server send an error: ";
                            //back to loginpage
                        break;
                        case "WARNING":
                            exp = "The operation you tried is not permitted, nothing happened. Reason: ";
                            //do nothing
                        break;
                        case "RESPONSE":
                            exp = "The server send a message back: ";
                            //do something with the received data
                        break;
                        default:
                            exp = "The server send an invalid message back: ";
                        break;
                    }
                    log(exp + msg[1]);
                    //alert (exp + msg);
                }
                STATE = 2;  //back to state 2 to receive normal messages
                break;
            }
        }
        
        SOCKET.onclose = function(){
            log('Socket Status: ' + SOCKET.readyState+' (Closed)');
            alert('De verbinding met de server is gesloten. Vernieuw de pagina om opnieuw te proberen.')
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

//post a changed setting to the server
function sendValue(name,value)
{      
    if(SOCKET.readyState == 1){
        var data = '{"'+name+'":"'+value+'"}';
        log("sending: " + data);
        STATE = 2;
        SOCKET.send(data);  
    }else{
        log('Socket Status: ' + SOCKET.readyState+' (Closed)');
        alert('De verbinding met de server is gesloten. Vernieuw de pagina om opnieuw te proberen.')
        STATE = 1;
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
