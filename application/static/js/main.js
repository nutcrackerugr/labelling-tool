var lastIndexBaseUrl = Math.max(window.location.pathname.indexOf("annotate"), window.location.pathname.indexOf("review"));
var baseurl = window.location.pathname.substring(0, lastIndexBaseUrl);
if (!baseurl.endsWith('/'))
	baseurl += '/';
	
var api = baseurl + "api/";

var last_tweet, last_user, labels = [], last_time = 0, automatic_order = false, already_annotated = true;

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
							console.info("Token renewed")
						},
						error: function()
						{
							alert("Your session has expired. Please log in again");
							window.location.replace(baseurl);
						}
					});
				}
			},
			success: function()
			{
				last_time = new Date();
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
					else if (data[key]["how"] == "extended_properties")
					{
						cls = data[key]["what"] == "1" ? "positive" : "neutral";
						css_cls = data[key]["what"] == "1" ? "list-group-item-success" : "list-group-item-info";
						
						var whys = "";
						if ($.isEmptyObject(data[key]["why"]))
							whys += "we do not have enough information yet"
						else
						{
							for (var wkey in data[key]["why"])
								whys += "For category <strong>" + wkey + "</strong>: " + data[key]["why"][wkey]["value_name"] + " (" + data[key]["why"][wkey]["value"] + ")<br/>";
							whys = whys.slice(0, -5);
						}
						
						$("#reasons").append("<button class=\"btn btn-primary\" type=\"button\" data-toggle=\"collapse\" data-target=\"#expandedPropertiesReasons\">Show Expanded Properties</button>");
						$("#reasons").append("<li class=\"list-group-item " + css_cls + " hanging-indent collapse\" id=\"expandedPropertiesReasons\">"
						                     + "This user's neighbourhood suggests the following " + Object.keys(data[key]["why"]).length + " properties:<br />"
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

function create_tweet(data)
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
						var checkboxes = $("input[name='label-" + key.replace(/ /g, "_") + "-option']");
						for (var number of data["labels"][key])
							$(checkboxes[number]).prop("checked", true);
					}
					else
						$("#label-" + key.replace(/ /g, "_") + '-select option[value="' + data["labels"][key] + '"]').prop("selected", true);
					
					$("#label-" + key.replace(/ /g, "_") + "-switch").prop("checked", true);
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
		$("#page").val(data["id"]);

		//Global variable
		last_tweet = data;
	}
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
		success: create_tweet,
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

function getRankedTweet(callback)
{
	if (already_annotated)
	{
		$("#logo").addClass("fa-spin");
		//If no tweet was specified, get the first unlabelled by querying with tid=0
		var url = api + "tweet/nextinrank";
			
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
			success: create_tweet,
			error: function()
			{
				alert("There was a problem loading the next tweet");
			},
			complete: function()
			{
				already_annotated = false;
				$("#logo").removeClass("fa-spin");

				if (callback)
					callback();
			}
		});
	}
	else
		alert("You need to annotate this tweet to continue with the next one");
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
	already_annotated = true;
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
	for (const label of labels)
		if ($("#label-" + label + "-switch").is(":checked"))
		{
			select = $("#label-" + label + "-select");
			if (select.length != 0)
				vlabels[label] = parseInt(select.val(), 10);
			else
			{
				selected_values = [];
				$.each($("input[name='label-" + label + "-option']:checked"), function() {
					selected_values.push(parseInt($(this).val(), 10));
				});

				vlabels[label] = selected_values;
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

function createLabelComponent(name, disclaimer, labeltag, options, bgcolorhex, help_text)
{
	if (!bgcolorhex)
		bgcolorhex = "f8f9fa";
	let html = "";

	if (!help_text || help_text === null)
		help_text = "No help available for this label";
	
	
	html += '<div class="row py-2 border-top" style="background-color: #' + bgcolorhex + ';">';
	html += '<div class="col">';
	
	if (disclaimer)
        html += '<div class="row"><div class="col"><div class="text-muted text-justify small-text mb-1">' + disclaimer + '</div></div></div>';
	
	html += '<div class="row"><div class="col-auto"><i class="fa fa-question-circle" data-toggle="tooltip" data-placement="left" title="' + help_text + '" /></div>';
	html += '<div class="col-auto"><span class="font-weight-bold">' + labeltag + '</span></div>';
	html += '<div class="col-auto"><div class="custom-control custom-switch align-middle">';
	html += '<input type="checkbox" class="custom-control-input" id="label-' + name.replace(/ /g, '_') + '-switch" checked>';
	html += '<label class="custom-control-label" for="label-' + name.replace(/ /g, '_') + '-switch">Save?</label></div></div></div>';
	html += '<div class="row"><div class="col">';
	html += options;
	html += '</div></div></div></div>'

	return html;
}

function createLabel(name, disclaimer, v)
{
	let labeltag = "", options = "";

	if (v["multiple"])
	{
		let option_value = 0;
		labeltag += '<label>' + v["name"] + "</label>";
		v["values"].split(",").forEach(function(item)
		{
			options += '<div class="form-check">';
			options += '<input class="form-check-input" type="checkbox" value="' + option_value++ + '" id="' + item.replace(/ /g, '_') + '" name="label-' + name.replace(/ /g, '_') + '-option">';
			options += '<label class="form-check-label" for="' + item.replace(/ /g, '_') + '">' + item + '</label>';
			options += '</div>';
		});
	}
	else
	{
		labeltag += '<label for="label-' + name.replace(/ /g, '_') + '-select">' + v["name"] + '</label>';
		options += '<select class="custom-select" id="label-' + name.replace(/ /g, '_') + '-select">';
		
		let option_value = 0;
		v["values"].split(",").forEach(function(item)
		{
			options += '<option value="' + option_value++ + '">' + item + '</option>';
		});
		
		options += '</select>';
	}

	return createLabelComponent(name, disclaimer, labeltag, options, v["bgcolorhex"], v["help_text"]);
}

$(function(){
	//Renew tokens if necessary
	setAuth();

	//Get labels and insert them in DOM
	$.ajax({
		beforeSend: setAuth,
		url: api + "labels",
		success: function(data)
		{
			labels = [];
			
			$.each(data, function(k, v)
			{
				let html = "", html2 = "", disclaimer='<i class="fa fa-exclamation-triangle" /> The following is a general category, just in case you cannot annotate specific ones. Leave blank otherwise';

				switch (v["kind"])
				{
					//Single-labels
					case 1:
						$("#single-labels").append(createLabel(v["name"], undefined, v));
						labels.push(v["name"].replace(/ /g, '_'));
						break;
					
					//Single-labels with disclaimer
					case 2:
						$("#single-labels").append(createLabel(v["name"], disclaimer, v));
						labels.push(v["name"].replace(/ /g, '_'));
						break;
					
					//Double-labels
					case 3:
						$("#double-labels-1").append(createLabel(v["name"], undefined, v));
						$("#double-labels-2").append(createLabel(v["name"] + "2", undefined, v));
						labels.push(v["name"].replace(/ /g, '_'));
						labels.push((v["name"] + "2").replace(/ /g, '_'));
						break;

					//Double-labels with disclaimer
					case 4:
						$("#double-labels-1").append(createLabel(v["name"], disclaimer, v));
						$("#double-labels-2").append(createLabel(v["name"] + "2", disclaimer, v));

						labels.push(v["name"].replace(/ /g, '_'));
						labels.push((v["name"] + "2").replace(/ /g, '_'));
						break;
				}
			});
		}
	});

	//Check if we are in rankedtagging or not
	var next_tweet_button = $("#next_tweet");
	if (next_tweet_button.length)
		automatic_order = true;
		

	//Get last labelled tweet
	if (automatic_order)
	{
		getRankedTweet();
		next_tweet_button.click(function(){getRankedTweet()});
	}
	else
	{
		if (typeof specific_tid !== "undefined")
			getTweet(specific_tid);
		else
			getTweet(0);
		
		$("#page").change(changePage);

		$("#firstunlabelled").click(function(){getTweet(0)}); //Called inside a lambda to avoid passing e to getTweet
	}

	$("#save_1, #save_2").click(save);
	$('[data-toggle="tooltip"]').tooltip();
	
	$(document).keydown(function(e)
	{
		switch (e.key)
		{
			case "ArrowRight":
			case "n":
				if (!automatic_order)
					$("#page").val(parseInt($("#page").val()) + 1).trigger("change");
				else
					getRankedTweet();
				break;
				
			case "ArrowLeft":
			case "p":
				if (!automatic_order)
					$("#page").val(parseInt($("#page").val()) - 1).trigger("change");
				break;
			
			case "s":
				$("#save_1").trigger("click");
				break;
				
			case "h":
				$("#keyboard_shortcuts").toggle();
		}
	});

	$("#tags").keydown(stopPropagation);
	$("#tweet_comment").keydown(stopPropagation);
	$("#page").keydown(stopPropagation);
});

