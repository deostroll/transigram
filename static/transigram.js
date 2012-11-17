var thisApp;

function _debug(msg, info){
	info = info || false;
	if(typeof window.console != undefined)
	{
		if(typeof _debug.debug == 'undefined')
			_debug.debug = true;
		if(typeof _debug.toggle == 'undefined')
			_debug.toggle = function(){
				_debug.debug = !_debug.debug;
			}
		if(_debug.debug == false) return;
				
		if(info)
			window.console.log(msg);
		else{
			var now = new Date();
			var time = now.toTimeString();
			time = time.substr(0, time.indexOf(' '));
			window.console.log(time + ': ' + msg);
		}
		
	}
}

(function(){
	var _onlyUrl = '/shouts';
	var isGettingShouts = false;
	var isPosting = false;
	var eventData = { 
		'postOperation':false,
		'data':null
	};
	
	var _username = null;
	var _content = null;
	var _lastID = null;
	thisApp = {
		'get': function(){			
			_debug("get() invoked");
			eventData.postOperation = false;
			if(isPosting) return;
			isGettingShouts = true;
			_debug(_lastID == ''? '<empty>': _lastID, true); 
			thisApp.xhr = $.ajax({
				url: _onlyUrl,
				type: "GET",
				data: _lastID != '' ? {'last_id': _lastID} : null,
				dataType: "json",
				success: function(data){
					_debug("get() callback");
					_debug(data, true);
					thisApp.refreshInternal(data);
					isGettingShouts = false;
				}
			});
		},
		'post': function() {	
			_debug("post() invoked");
			if (isGettingShouts){
				_debug("aborting request");
				thisApp.xhr.abort();
			}
			isPosting = true;
			thisApp.appSubmit();
			$.ajax({
				url: _onlyUrl,
				data: {
					username: _username,
					content: _content
				},
				type: "POST",
				success: function(data){
					_debug("post() callback invoked");
					thisApp.refreshInternal(data);
					isPosting = false;
				}
			});
		},
		'setEvents': function(e){
			thisApp.refreshEvent = e.onRefresh;
			thisApp.appStart = e.onStart;
			thisApp.appSubmit = e.onSubmit;
			thisApp.statusCallback = e.onStatusCallback;
		},
		'refreshInternal': function(data){
			eventData.data = data;
			thisApp.refreshEvent(eventData);
			isGettingShouts = false;	
		},
		'start': function(){
			thisApp.appStart();
			window.setTimeout(function(){
				window.setInterval(function(){
					_debug("__ get interval clocked");
					thisApp.get();
					}, 10*1000);
			}, 5000);
			window.setInterval(function(){
				_debug("__ status interval clocked");
				var obj = { posting: isPosting, getting: isGettingShouts};
				if(thisApp.statusCallback)
					thisApp.statusCallback(obj);
			}, 5*1000);
		},
		'set': function(obj){
			_username = obj.username;
			_content = obj.content;
		},
		'setLastId': function(id){
			_lastID = id;
		}
	};
})();

