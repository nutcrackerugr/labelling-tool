var baseurl = window.location.pathname.replace("tagging", "");
if (!baseurl.endsWith('/'))
	baseurl += '/';
	
var api = baseurl + "api/";

var last_tweet, last_user, labels = {}, labels_name = {}, last_time= new Date();

function stopPropagation(e)
{
	//~ e.preventDefault();
	e.stopImmediatePropagation();
	//~ e.cancelBubble = true;
	//~ return false;
}

function setAuth(xhr)
{
	if (Math.floor((new Date() - last_time) / 60000) >= 5)
	{
		$.ajax({
			async: false,
			type: "GET",
			url: api + "auth/token/valid",
			error: function(xhr)
			{
				if (xhr.status == 403)
				{
					$.ajax({
						async: false,
						type: "POST",
						url: api + "auth/token/refresh",
						headers: {
							"X-CSRF-TOKEN": Cookies.get("csrf_refresh_token")
						},
						success: function()
						{
							last_time = new Date();
						},
						error: function()
						{
							alert("Your session has expired. Please log in again");
							window.location.replace(baseurl);
						}
					});
				}
			}
		});
	}

	return true;
}

function createText(text, highlights, aihighlights, callback)
{
	var html = "";
	var words = text.split(" ");
	
	if (!highlights)
		highlights = [];
		
	if (!aihighlights)
		aihighlights = [];
	
	for (var i = 0; i < words.length; ++i)
		if (highlights.includes(words[i]) && aihighlights.includes(words[i]))
			html += '<span class="clickable selected aiselected">' + words[i] + '</span> ';
		else
			if (highlights.includes(words[i]))
				html += '<span class="clickable selected">' + words[i] + '</span> ';
			else
				if (aihighlights.includes(words[i]))
					html += '<span class="clickable aiselected">' + words[i] + '</span> ';
				else
					html += '<span class="clickable">' + words[i] + '</span> ';
	
	$("#tweet_content").html(html);
	$("#tweet_content span.clickable").click(span_click);
	
	if (callback)
		callback();
}

function span_click(e)
{
	$(this).toggleClass("selected");
}

function save_highlights(callback)
{
	vhighlights = []
	$("#tweet_content span.selected").each(function()
	{
		vhighlights.push($(this).html());
	});
	
	$.ajax({
		beforeSend: setAuth,
		type: "POST",
		url: api + "tweet/" + last_tweet["id"] + "/update/highlights",
		headers: {
			"X-CSRF-TOKEN": Cookies.get("csrf_access_token")
		},
		data: JSON.stringify(vhighlights),
		contentType:"application/json",
		dataType: "json",
		success: callback
	});
}

function getReasons(n, callback)
{	
	$.ajax({
		beforeSend: setAuth,
		type: "GET",
		url: api + "tweet/" + parseInt(n, 10) + "/suggestions",
		success: function(data)
		{
			if ($.isEmptyObject(data))
				alert("There are no reasons for this tweet");
			else
			{
				$("#reasons").empty();
				
				for (var key in data)
				{
					if (data[key]["how"] == "ontology")
					{
						cls = data[key]["what"] == "1" ? "positive" : "neutral";
						css_cls = data[key]["what"] == "1" ? "list-group-item-success" : "list-group-item-info";
						
						var whys = "";
						if ($.isEmptyObject(data[key]["why"]))
							whys += "nothing"
						else
						{
							for (var wkey in data[key]["why"])
								whys += data[key]["why"][wkey][1] + "::<strong>" + data[key]["why"][wkey][0] + "</strong><br/>";
							whys = whys.slice(0, -5);
						}
						
						
						$("#reasons").append("<li class=\"list-group-item " + css_cls + " hanging-indent\" \">"
						                     + "Using the ontology " + key + ", the following " + data[key]["why"].length + " words were found:<br />"
						                     + whys + " </li>"
						                    );
					}
					else
						$("#reasons").append("<li class=\"list-group-item " + css_cls + " hanging-indent\" data-toggle=\"tooltip\" data-placement=\"right\" title=\"Reasons: " + whys + "\">"
						                     + "Using " + key + " (" + data[key]["how"] + "): suggests " + cls + " because of the following reasons: " + data[key]["why"] + " </li>");
				}
			}
			
			$('[data-toggle="tooltip"]').tooltip()
		},
		complete: callback
	});
}

function getOtherTweets(uid, callback)
{
	$.ajax({
		beforeSend: setAuth,
		type: "GET",
		url: api + "user/" + uid + "/tweets/5",
		success: function(data)
		{
			$("#othertweets").empty();
			$.each(data, function(k, v)
			{
				$("#othertweets").append("<li class=\"list-group-item\">" + v["full_text"] + "</li>");
			});
		}
	});
}

function getTweet(n, callback)
{
	n = !n ? 0 : n;
	var url = api + "tweet/" + n;
		
	$.ajax({
		beforeSend: setAuth,
		type: "GET",
		url: url,
		statusCode: {
			403: function(xhr)
			{
				alert("Your session has expired. Please log in again");
				window.location.replace(baseurl);
			}
		},
		success: function(data)
		{
			if ($.isEmptyObject(data))
				alert("The tweet " + n + " does not exists");
			else
			{
				$.ajax({
					beforeSend: setAuth,
					type: "GET",
					url: api + "user/" + data["user"],
					success: function(userdata)
					{
						$("#user_description").html(userdata["description"]);
						$("#user_profile_pic").attr("src", userdata["profile_image_url_https"]);
						$("#user_name").html(userdata["name"] + ' <span class="text-secondary">@' + userdata["screen_name"] + '</span>');
						last_user = userdata;
					}
				});
				
				createText(data["full_text"], data["highlights"], data["aihighlights"]);
				$("input:checkbox").prop("checked", false);
				for (var key in data["labels"])
				{
					$("#" + labels_name[key] + "select option[value=\"" + data["labels"][key] + "\"]").prop("selected", true);
					$("#" + labels_name[key] + "switch").prop("checked", true);
				}
				
				$("#tweet_comment").val(data["comment"] ? data["comment"] : "");
				
				if (!$.isEmptyObject(data["tags"]))
					$("#tags").val(data["tags"].join(','));
				else
					$("#tags").val("");
				
				getReasons(data["id"]);
				getOtherTweets(data["user"]);
				
				
				if (!n || n == 0)
					$("#page").val(data["id"]);
					
				last_tweet = data;
			}
		},
		error: function()
		{
			if (n && n != 0)
				alert("The tweet " + n + " does not exists");
			else
			{
				alert("There are not unlabelled tweets");
				$("#page").val(1);
				getTweet(1);
			}
		},
		complete: callback
	});
}

function changePage(e)
{
	var elem = $(this)
	//elem.prop("disabled", true);
	getTweet(elem.val());//, function()
	//~ {
		//~ elem.prop("disabled", false);
	//~ });
}

function save_labels(callback)
{
	vlabels = {}
	for (var key in labels)
		if ($("#" + key + "switch").is(":checked"))
			vlabels[labels[key]] = parseInt($("#" + key + "select").val(), 10);
	
	$.ajax({
		beforeSend: setAuth,
		type: "POST",
		url: api + "tweet/" + last_tweet["id"] + "/update/labels",
		headers: {
			"X-CSRF-TOKEN": Cookies.get("csrf_access_token")
		},
		data: JSON.stringify(vlabels),
		contentType:"application/json",
		dataType: "json",
		success: function()
		{
			$.ajax({
				beforeSend: setAuth,
				type: "POST",
				url: api + "tweet/" + last_tweet["id"] + "/update/tags",
				headers: {
					"X-CSRF-TOKEN": Cookies.get("csrf_access_token")
				},
				data: JSON.stringify($("#tags").val().split(',')),
				contentType: "application/json",
				dataType: "json",
				success: function()
				{
					$.ajax({
						beforeSend: setAuth,
						type: "POST",
						url: api + "tweet/" + last_tweet["id"] + "/update/comment",
						headers: {
							"X-CSRF-TOKEN": Cookies.get("csrf_access_token")
						},
						data: {"comment": $("#tweet_comment").val()},
						success: callback
					});
				}
			});
		}
	});
}


//~ function getUnlabelledTweet()
//~ {
	//~ $.getJSON(api + "get_tweet/", function(data)
	//~ {
		//~ if ($.isEmptyObject(data))
			//~ alert("There are no more unlabelled tweets :))");
		//~ else
		//~ {
			//~ $.getJSON(api + "get_user/" + data["user"], function(userdata)
			//~ {
				//~ $("#user_description").html(userdata["description"]);
				//~ $("#user_profile_pic").attr("src", userdata["profile_image_url_https"]);
				//~ $("#user_name").html(userdata["name"] + ' <span class="text-secondary">@' + userdata["screen_name"] + '</span>');
				//~ last_user = userdata;
			//~ });
			
			//~ createText(data["full_text"], data["highlights"], data["aihighlights"]);
			//~ $("input:checkbox").prop("checked", false);
			//~ for (var key in data["labels"])
			//~ {
				//~ $("#" + labels_name[key] + "select option[value=\"" + data["labels"][key] + "\"]").prop("selected", true);
				//~ $("#" + labels_name[key] + "switch").prop("checked", true);
			//~ }
			
			//~ $("#page").val(data["id"]);
			//~ last_tweet = data;
		//~ }
	//~ });
//~ }

function save(e)
{
	var elem = $(this);
	elem.prop("disable", true).html('<i class="fa fa-spinner fa-spin" aria-hidden="true"></i>');
	
	function success(){
		elem.prop("disable", false).html('<i class="fa fa-check" aria-hidden="true"></i>');
		setTimeout(function()
		{
			elem.html("Save Changes");
		}, 1000);
	}
	
	save_highlights();
	save_labels(success);
}

$(function(){
	//~ if (!localStorage.jwt_access)
		//~ window.location.replace(baseurl);
	
	$.ajax({
		beforeSend: setAuth,
		url: api + "labels",
		success: function(data)
		{
			labels = {}
			var html = "";
			
			$.each(data, function(k, v)
			{
				labels["label" + (k+1)] = v["name"];
				labels_name[v["name"]] = "label" + (k+1);
				html += '<div class="form-group mb-2 d-flex align-items-end">';
				html += '<div class="mr-auto">';
				html += '<label for="label' + (k+1) + 'select">' + v["name"] + ':</label>';
				html += '<select class="custom-select" id="label' + (k+1) + 'select">';
				
				var option_value = 0;
				v["values"].split(",").forEach(function(item)
				{
					html += '<option value="' + option_value++ + '">' + item + '</option>';
				});
				
				
				//~ html += '<option value="-1">Negative</option>';
				//~ html += '<option value="0">Neutral</option>';
				//~ html += '<option value="1">Positive</option>';
				html += '</select>';
				html += '</div>';
				html += '<div>';
				html += '<div class="custom-control custom-switch align-middle">';
				html += '<input type="checkbox" class="custom-control-input" id="label' + (k+1) + 'switch" checked>';
				html += '<label class="custom-control-label" for="label' + (k+1) + 'switch">Save?</label>';
				html += '</div>';
				html += '</div>';
				html += '</div>';
			});
			
			//~ html += '<button type="submit" class="btn btn-primary mt-2" id="savelabels">Save</button>';
			
			$("#labelform").html(html);//.append($("<button/>", {"class": "btn btn-primary mt-2", "text": "Save", "id":"savelabels"}).click(savelabels));
			//~ $("#labelform").append(
				//~ $("<div/>", {"class": "form-group"}).append(
					//~ $("<label/>", {"for": "tweet_comment", "text":"Comment:"})
				//~ ).append(
					//~ $("<textarea/>", {"class": "form-control", "id":"tweet_comment"})
				//~ )
			//~ );
		}
	});
	
	getTweet(0);
	$("#page").change(changePage);
	$("#firstunlabelled").click(function(){getTweet(0)}); //Called inside a lambda to avoid passing e to getTweet
	$("#save").click(save);
	$('[data-toggle="tooltip"]').tooltip();
	
	$(document).keydown(function(e)
	{
		switch (e.key)
		{
			case "ArrowRight":
			case "n":
				$("#page").val(parseInt($("#page").val()) + 1).trigger("change");
				break;
				
			case "ArrowLeft":
			case "p":
				$("#page").val(parseInt($("#page").val()) - 1).trigger("change");
				break;
			
			case "s":
				$("#save").trigger("click");
				break;
				
			case "h":
				$("#keyboard_shortcuts").toggle();
		}
	});

	$("#tags").keydown(stopPropagation);
	$("#tweet_comment").keydown(stopPropagation);
	$("#page").keydown(stopPropagation);
});

