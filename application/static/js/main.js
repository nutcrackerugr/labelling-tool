var baseurl = window.location.pathname.replace("tagging", "");
if (!baseurl.endsWith('/'))
	baseurl += '/';
	
var api = baseurl + "api/";

var last_tweet, last_user, labels = {}, labels_name = {}, last_time= new Date();

function stopPropagation(e)
{
	e.stopImmediatePropagation();
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
				if (xhr.status == 403 || xhr.status == 401)
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
	$("#logo").addClass("fa-spin");
	//If no tweet was specified, get the first unlabelled by querying with tid=0
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
				alert("There was a problem loading the tweet " + n);
			else
			{
				url = api + "tweet/" + data["id"];
				//Get author details
				$.ajax({
					beforeSend: setAuth,
					type: "GET",
					url: api + "user/" + data["user"],
					statusCode: {
						403: function(xhr)
						{
							alert("Your session has expired. Please log in again");
							window.location.replace(baseurl);
						}
					},
					success: function(userdata)
					{
						$("#user_description").html(userdata["description"]);
						$("#user_profile_pic").attr("src", userdata["profile_image_url_https"]);
						$("#user_name").html(userdata["name"] + ' <span class="text-secondary">@' + userdata["screen_name"] + '</span>');
						last_user = userdata;
					}
				});

				//Get last annotation details
				$.ajax({
					beforeSend: setAuth,
					type: "GET",
					url: url + "/annotation",
					statusCode: {
						403: function(xhr)
						{
							alert("Your session has expired. Please log in again");
							window.location.replace(baseurl);
						}
					},
					success: function(annotationdata)
					{
						data["highlights"] = annotationdata["highlights"];
						data["aihighlights"] = annotationdata["aihighlights"];
						data["labels"] = annotationdata["labels"];
						data["tags"] = annotationdata["tags"];
						data["comment"] = annotationdata["comment"];

						$("#last_annotation").html("Last annotation on " + annotationdata["timestamp"]);// + " by " + annotationdata["appuser"]["username"]);
					},
					error: function()
					{
						data["highlights"] = [];
						data["aihighlights"] = [];
						data["labels"] = [];
						data["tags"] = [];
						data["comment"] = undefined;

						$("#last_annotation").html("There are not previous annotations for this tweet");
					},
					complete: function()
					{
						//Draw tweet text adding the highlight-with-click feature
						createText(data["full_text"], data["highlights"], data["aihighlights"]);

						//Save-switch to false for all the tags
						$("input:checkbox").prop("checked", false);

						//Save-switch to true for all existing tags
						for (var key in data["labels"])
						{
							if (typeof data["labels"][key] == "object")
							{
								var checkboxes = $("input[name='" + key + "']");
								for (var number of data["labels"][key])
									$(checkboxes[number]).prop("checked", true);
							}
							else
								$("#" + labels_name[key] + "select option[value=\"" + data["labels"][key] + "\"]").prop("selected", true);
							
							$("#" + labels_name[key] + "switch").prop("checked", true);
						}

						//Write comment
						$("#tweet_comment").val(data["comment"] ? data["comment"] : "");

						//Collection of tags to string
						if (!$.isEmptyObject(data["tags"]))
							$("#tags").val(data["tags"].join(','));
						else
							$("#tags").val("");
					}
				});

				//Get assistants info and other tweets
				getReasons(data["id"]);
				getOtherTweets(data["user"]);
				

				//Set tweet number
				if (!n || n == 0)
					$("#page").val(data["id"]);

				//Global variable
				last_tweet = data;
			}
		},
		error: function()
		{
			if (n && n != 0)
				alert("There was a problem loading the tweet " + n);
			else
			{
				alert("There are not unlabelled tweets");
				$("#page").val(1);
				getTweet(1);
			}
		},
		complete: function()
		{
			$("#logo").removeClass("fa-spin");

			if (callback)
				callback();
		}
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

function save_all(callback)
{
	var url = api + "tweet/" + last_tweet["id"];
	
	//Data
	payload = {}

	//Highlighted words
	vhighlights = []
	$("#tweet_content span.selected").each(function()
	{
		vhighlights.push($(this).html());
	});
	payload["highlights"] = vhighlights;

	//Annotation values
	vlabels = {}
	for (var key in labels)
		if ($("#" + key + "switch").is(":checked"))
		{
			select = $("#" + key + "select");
			if (select.length != 0)
				vlabels[labels[key]] = parseInt(select.val(), 10);
			else
			{
				selected_values = [];
				$.each($("input[name='" + labels[key] + "']:checked"), function() {
					selected_values.push(parseInt($(this).val(), 10));
				});

				vlabels[labels[key]] = selected_values;
			}
		}
	
	payload["labels"] = vlabels;

	//Tags and comment
	payload["tags"] = $("#tags").val().split(',');
	payload["comment"] = $("#tweet_comment").val();

	$.ajax({
		beforeSend: setAuth,
		type: "POST",
		url: url + "/annotation/create",
		statusCode: {
			403: function(xhr)
			{
				alert("Your session has expired. Please log in again");
				//~ window.location.replace(baseurl);
			}
		},
		headers: {
			"X-CSRF-TOKEN": Cookies.get("csrf_access_token")
		},
		data: JSON.stringify(payload),
		contentType: "application/json",
		dataType: "json",
		success: callback
	});
}

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
	
	save_all(success);
}

$(function(){
	//Get labels and insert them in DOM
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

				if (v["bgcolorhex"])
				{
					html += '<div class="text-muted text-justify small-text p-1 border-top" style="background-color:#' + v["bgcolorhex"] + '"><i class="fa fa-exclamation-triangle" /> The following is a general category, just in case you cannot annotate specific ones. Leave blank otherwise</div>'
					html += '<div class="form-group mb-2 d-flex align-items-end p-1" style="background-color:#' + v["bgcolorhex"] + '">';
				}
				else
					html += '<div class="form-group mb-2 d-flex align-items-end p-1 border-top">';
				
				html += '<div class="mr-auto">';
				
				if (v["multiple"])
				{
					var option_value = 0;
					html += '<label>' + v["name"] + "</label>";
					v["values"].split(",").forEach(function(item)
					{
						html += '<div class="form-check">';
						html += '<input class="form-check-input" type="checkbox" value="' + option_value++ + '" id="' + item + '" name="' + v["name"] + '">';
						html += '<label class="form-check-label" for="' + item + '">' + item + '</label>';
						html += '</div>';
					});
				}
				else
				{
					html += '<label for="label' + (k+1) + 'select">' + v["name"] + ':</label>';
					html += '<select class="custom-select" id="label' + (k+1) + 'select">';
					
					var option_value = 0;
					v["values"].split(",").forEach(function(item)
					{
						html += '<option value="' + option_value++ + '">' + item + '</option>';
					});
					
					html += '</select>';
				}

				html += '</div>';
				html += '<div>';
				html += '<div class="custom-control custom-switch align-middle">';
				html += '<input type="checkbox" class="custom-control-input" id="label' + (k+1) + 'switch" checked>';
				html += '<label class="custom-control-label" for="label' + (k+1) + 'switch">Save?</label>';
				html += '</div>';
				html += '</div>';
				html += '</div>';
			});
			
			$("#labelform").html(html);
		}
	});

	//Get last labelled tweet
	getTweet(0);
	$("#page").change(changePage);

	//Assign event handlers
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

