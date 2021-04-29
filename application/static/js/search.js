var lastIndexBaseUrl = window.location.pathname.indexOf("search");
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

function createSearchResults(data)
{
	if ($.isEmptyObject(data))
		alert("There are not any results")
	else
	{
		$("#cards").empty();
		$.each(data, function(k, v)
		{
			$("#cards").append('<div class="card p-3 rounded tweetcard"> \
				<div class="card-body"> \
				<p>' + v["full_text"] + '</p>\
				<a href="review/' + v["id"] + '" class="card-link">Review this tweet</a>\
				</div></div>');
		});
	}
}

function search(q, callback)
{
	$("#logo").addClass("fa-spin");

	$.ajax({
		beforeSend: setAuth,
		type: "GET",
		url: api + "tweet/findByKeywords/?q=" + encodeURIComponent(q),
		statusCode: {
			403: function(xhr)
			{
				alert("Your session has expired. Please log in again");
				window.location.replace(baseurl);
			}
		},
		success: createSearchResults,
		error: function()
		{
			alert("There was a problem while searching");
		},
		complete: function()
		{
			$("#logo").removeClass("fa-spin");

			if (callback)
				callback();
		}
	});
}

function exec_search(e)
{
	var q = $("#searchinput").val().trim();
	
	if (q.length > 0)
		search(q);
		
		e.stopImmediatePropagation();
		e.preventDefault()
		return false;
}

$(function(){
	//Renew tokens if necessary
	setAuth();
	
	//Exec search
	$("#searchbutton").click(exec_search);
	$("#searchform").submit(exec_search);
});

