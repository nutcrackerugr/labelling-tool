var lastIndexBaseUrl = Math.max(window.location.pathname.indexOf("annotate"), window.location.pathname.indexOf("review"));
var baseurl = window.location.pathname.substring(0, lastIndexBaseUrl);
if (!baseurl.endsWith('/'))
	baseurl += '/';
	
var api = baseurl + "api/";

var last_time = 0, last_ua;

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

function getUserAnnotation()
{
	$.ajax({
		beforeSend: setAuth,
		type: "GET",
		url: api + "user/annotation/unreviewed",
		success: createUserAnnotationComponent
	});
}

function reviewAnnotation(decision)
{
	$(".btn").prop("disabled", true);
	$("#logo").addClass("fa-spin");
	let payload = {
		"user_id": last_ua["user_id"],
		"appuser_id" : last_ua["appuser_id"],
		"timestamp": last_ua["timestamp"],
		"decision": decision
	};

	$.ajax({
		beforeSend: setAuth,
		type: "POST",
		url: api + "user/annotation/review",
		statusCode: {
			403: function(xhr)
			{
				alert("Your session has expired. Please log in again");
				window.location.replace(baseurl);
			},
			500: function(xhr)
			{
				alert(xhr.responseJSON["message"]);
			},
		},
		headers: {
			"X-CSRF-TOKEN": Cookies.get("csrf_access_token")
		},
		data: JSON.stringify(payload),
		contentType: "application/json",
		dataType: "json",
		success: getUserAnnotation
	});
}

function createUserAnnotationComponent(ua)
{
	if (!$.isEmptyObject(ua))
	{
		last_ua = ua;
		$("#ua_list").empty();
		let html = "";

		$.ajax({
			beforeSend: setAuth,
			type: "GET",
			url: api + "user/" + ua["user_id"],
			success: function(user)
			{
				html += '<div class="card p-3 rounded tweetcard">';
				html += '<div class="card-body">';
				html += '<div class="d-flex flex-row">'
				html += '<img class="mr-3 profile-pic float-left" alt="User Image" src="' + user["profile_image_url_https"] + '" />';
				html += '<div>';
				html += '<h5 class="mt-0">' + user["name"] + ' <span class="text-secondary">@' + user["screen_name"] + '</span></h5>';
				html += '<h6 class="mt-0 text-secondary">User Description:</h6>';

				if (user["description"] === null)
					user["description"] = "Not available";

				html += '<p>' + user["description"] + '</p>';
				html += '</div>';
				html += '</div>';
				html += '<h6 class="mt-0 text-secondary">Tweets:</h6>';
				
				$.ajax({
					beforeSend: setAuth,
					type: "GET",
					url: api + "user/" + ua["user_id"] + "/tweets/10",
					success: function(tweets)
					{
						$.each(tweets, function(k, v)
						{
							html += '<p class="p-2 rounded border border-dark">' + v["full_text"] + '</p>';
						});
					},
					complete: function()
					{
						html += '</div>';
						html += '</div>';
						html += '<div class="card mt-4 p-3 rounded list-group-item-success">'
						html += 'This user\'s neighbourhood suggests the following properties:';
						html += '<ul>';

						$.each(ua["extended_labels"], function(k, v)
						{
							let position = "neutral";
							if (v < 0) position = "negative";
							if (v > 0) position = "positive";

							html += '<li><strong>' + k + ': ' + position + '</strong> (' + v + ')</li>';
						});

						html += '</ul>'
						html += '<div class="btn-group">';
						html += '<button type="button" class="btn btn-outline-danger"  onclick="reviewAnnotation(-1)">Definitely wrong</button>';
						html += '<button type="button" class="btn btn-outline-primary" onclick="reviewAnnotation(0)">I cannot confirm or deny</button>';
						html += '<button type="button" class="btn btn-outline-success" onclick="reviewAnnotation(1)">Seems right</button>';
						html += '</div>';
						$("#ua_list").append(html);
						$("#logo").removeClass("fa-spin");
					}
				});
			}
		});
	}
	else
	{
		let html = "";
		html += '<div class="card mt-4 p-3 rounded list-group-item-success">'
		html += 'There are no more automatic annotations to check! Please come back tomorrow :)';
		html += '</div>';
		$("#ua_list").empty().append(html);
		$("#logo").removeClass("fa-spin");
	}
}

$(function(){
	//Renew tokens if necessary
	setAuth();

	$("#logo").addClass("fa-spin");
	getUserAnnotation();
});

