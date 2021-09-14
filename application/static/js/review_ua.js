var lastIndexBaseUrl = window.location.pathname.indexOf("check_ua");
var baseurl = window.location.pathname.substring(0, lastIndexBaseUrl);
if (!baseurl.endsWith('/'))
	baseurl += '/';
	
var api = baseurl + "api/";

var last_time = 0, last_ua, step = 0;

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

function getUserAnnotation(uid)
{
	if (uid)
		$.ajax({
			beforeSend: setAuth,
			type: "GET",
			url: api + "user/" + uid + "/annotation",
			success: createRevisitUserAnnotationComponent,
			error: createNoMoreAnnotationsWarning
		});
	else
		if (validate === 1) //html previous script global
			$.ajax({
				beforeSend: setAuth,
				type: "GET",
				url: api + "userAnnotation/findByStatus/?status=unvalidated&decision=-1",
				success: createRevisitUserAnnotationComponent,
				error: createNoMoreAnnotationsWarning
			});
		else
			$.ajax({
				beforeSend: setAuth,
				type: "GET",
				url: api + "userAnnotation/",
				success: createUserAnnotationComponent,
				error: createNoMoreAnnotationsWarning
			});
}

function getUnreviewedUserAnnotation()
{
	return getUserAnnotation();
}

function reviewAnnotation(decision)
{
	console.log("review!")
	if (last_ua)
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
			type: "PUT",
			url: api + "userAnnotation/",
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
			success: getUnreviewedUserAnnotation
		});
	}
}


function nextQuestionStep(step, decision)
{
	switch (step)
	{
		case 0:
			if (decision === 1)
			{
				reviewAnnotation(-1); //Definitely wrong
				return 0; //Restart
			}
			else
				return 1; //Go to step 1

			break;
		
		case 1:
			if (decision === 1)
				return 2; //Go to step 2
			else
			{
				reviewAnnotation(0); //I cannot confirm or deny
				return 0; //Restart
			}
				
			break;
		
		case 2:
			if (decision === 1)
				reviewAnnotation(-1); //Definitely wrong
			else
				reviewAnnotation(1); //Looks right

			return 0; //Restart in both scenarios
			
			break;
	}
}

function answerForCurrentStep(decision)
{
	let q = $("#question").fadeOut("fast");
	step = nextQuestionStep(step, decision);

	if (step != 0)
	{
		q.html(questionForStep(step));
		q.fadeIn("fast");
	}
	else
	{
		$("#decisionCard").hide();
	}
}

function questionForStep(step)
{
	let question;

	switch (step)
	{
		case 0:
			question = "Is there any evidence that at least one property is <strong>incorrect</strong>?";
			break;
		case 1:
			question = "Is there any evidence that at least one property is <strong>correct</strong>?";
			break;
		case 2:
			question = "Is there any <strong>contradiction</strong>? Remember to check the guidelines if you are not sure";
			break;
		default:
			question = "Oh no... this is an unexpected error. Please contact support. Thank you."
	}

	return question;
}

function createNoMoreAnnotationsWarning()
{
	let html = "";
	html += '<div class="card mt-4 p-3 rounded list-group-item-success">'
	html += 'There are no more automatic annotations to check! Please come back tomorrow :)';
	html += '</div>';
	$("#ua_list").empty().append(html);
	$("#logo").removeClass("fa-spin");
}

function createUserAnnotationComponent(ua)
{
	if (!$.isEmptyObject(ua))
	{
		last_ua = ua;
		$("#page").val(ua["user_id"]);
		$("#ua_list").empty();
		let html = "";

		html += '<div class="card p-3 rounded tweetcard">';
		html += '<div class="card-body">';
		html += '<div class="d-flex flex-row">';
		html += '<div id="user_image"></div>';
		html += '<div id="user_info"></div>';
		html += '</div>';
		html += '<h6 class="mt-0 text-secondary">Tweets:</h6>';
		
		$.ajax({
			beforeSend: setAuth,
			type: "GET",
			url: api + "user/" + ua["user_id"] + "/tweets/?limit=15",
			success: function(tweets)
			{
				$.each(tweets, function(k, v)
				{
					html += '<p class="p-2 rounded border border-dark">' + v["full_text"] + '<br class="link-to-original" /><span class="mt-0 text-secondary link-to-original">Tweet ID: ' + v["id_str"] + '</span>&nbsp;&nbsp;<a href="https://twitter.com/a/status/' + v["id_str"] + '" class="link-to-original">Link to original</a></p>';
				});
			},
			complete: function()
			{
				html += '</div>';
				html += '</div>';
				html += '<div class="card mt-4 p-3 rounded list-group-item-success" id="decisionCard">'
				html += 'This user\'s neighbourhood suggests the following properties:';
				html += '<ul>';

				$.each(ua["extended_labels"], function(k, v)
				{
					if (k.indexOf("symbol_") == -1)
					{
						// if (k == "alpha")
						// 	html += '<li><strong>Importance (alpha): </strong> ' + v + '</li>';
						// else
						// {
						// 	let position = "neutral";
						// 	if (v < 0) position = "negative";
						// 	if (v > 0) position = "positive";
						// 	html += '<li><strong>' + k + ': ' + position + '</strong> (' + v + ')&emsp;<strong>Confidence:</strong> ' + ua["extended_labels"]["symbol_confidence_" + k] + '</li>';
						// }

						if (k != "alpha")
						{
							let position = "neutral or without information";
							if (v < 0) position = "negative";
							if (v > 0) position = "positive";

							html += '<li><strong>' + k + ': ' + position + '</strong></li>';
						}
					}
				});

				html += '</ul>'

				step = 0;
				html += '<span class="question" id="question">' + questionForStep(step) +'</span>';
				html += '<div class="btn-group" id="answers">';
				html += '<button type="button" class="btn btn-outline-danger"  onclick="answerForCurrentStep(0)">No</button>';
				html += '<button type="button" class="btn btn-outline-success" onclick="answerForCurrentStep(1)">Yes</button>';
				html += '<button type="button" class="btn btn-outline-secondary" onclick="reviewAnnotation(-99)">I do not know, skip</button>';
				html += '</div>';
				$("#ua_list").append(html);

				$.ajax({
					beforeSend: setAuth,
					type: "GET",
					url: api + "user/" + ua["user_id"],
					success: function(user)
					{
						$("#user_image").append('<img class="mr-3 profile-pic float-left" alt="User Image" src="' + user["profile_image_url_https"] + '" />')
						$("#user_info").append('<p class="text-secondary mt-0">User ID: ' + user["id_str"] + '</p>');
						$("#user_info").append('<h5 class="mt-0">' + user["name"] + ' <span class="text-secondary">@' + user["screen_name"] + '</span></h5>');
						$("#user_info").append('<h6 class="mt-0 text-secondary">User Description:</h6>');
						$("#user_info").append('<p>' + user["description"] === null ? "Not available" : user["description"] + '</p>');

						$(".link-to-original").show()
					}
				});

				$("#logo").removeClass("fa-spin");
			}
		});
	}
	else
		createNoMoreAnnotationsWarning()
}

function createRevisitUserAnnotationComponent(ua)
{
	if (!$.isEmptyObject(ua))
	{
		$("#ua_list").empty();
		$("#page").val(ua["user_id"]);
		last_ua = ua;
		let html = "";

		html += '<div class="card p-3 rounded tweetcard">';
		html += '<div class="card-body">';
		html += '<div class="d-flex flex-row">';
		html += '<div id="user_image"></div>';
		html += '<div id="user_info"></div>';
		html += '</div>';
		html += '<h6 class="mt-0 text-secondary">Tweets:</h6>';
		
		$.ajax({
			beforeSend: setAuth,
			type: "GET",
			url: api + "user/" + ua["user_id"] + "/tweets/?limit=15",
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
					if (k.indexOf("symbol_") == -1)
					{
						// if (k == "alpha")
						// 	html += '<li><strong>Importance (alpha): </strong> ' + v + '</li>';
						// else
						// {
						// 	let position = "neutral";
						// 	if (v < 0) position = "negative";
						// 	if (v > 0) position = "positive";
						// 	html += '<li><strong>' + k + ': ' + position + '</strong> (' + v + ')&emsp;<strong>Confidence:</strong> ' + ua["extended_labels"]["symbol_confidence_" + k] + '</li>';
						// }

						if (k != "alpha")
						{
							let position = "neutral or without information";
							if (v < 0) position = "negative";
							if (v > 0) position = "positive";

							html += '<li><strong>' + k + ': ' + position + '</strong></li>';
						}
					}
				});

				html += '</ul>'
				html += '<div class="btn-group">';

				if (ua["reviewed"])
					switch (ua["decision"])
					{
						case -1:
							html += '<button type="button" class="btn btn-danger">Decision was Definitely wrong by ' + ua["reviewed_by"] +  '</button>';
							break;
						
						case 0:
							html += '<button type="button" class="btn btn-primary">Decision was I cannot confirm or deny by ' + ua["reviewed_by"] +  '</button>';
							break;
						
						case 1:
							html += '<button type="button" class="btn btn-success">Decision was Looks Right by ' + ua["reviewed_by"] +  '</button>';
							break;
					}
				else
					html += '<button type="button" class="btn btn-secondary">Not reviewed yet</button>';
				
				html += '</div>';
				
				if (validate === 1)
				{
					html += '<div class="btn-group">';
					html += '<button type="button" class="btn btn-outline-danger"  onclick="reviewAnnotation(-1)">Definitely wrong</button>';
					html += '<button type="button" class="btn btn-outline-primary" onclick="reviewAnnotation(0)">I cannot confirm or deny</button>';
					html += '<button type="button" class="btn btn-outline-success" onclick="reviewAnnotation(1)">Looks right</button>';
					html += '</div>';
				}

				html += '<span class="text-secondary">Press Resume Work to continue with annotations</span>';
				$("#ua_list").append(html);

				$.ajax({
					beforeSend: setAuth,
					type: "GET",
					url: api + "user/" + ua["user_id"],
					success: function(user)
					{
						$("#user_image").append('<img class="mr-3 profile-pic float-left" alt="User Image" src="' + user["profile_image_url_https"] + '" />')
						$("#user_info").append('<h5 class="mt-0">' + user["name"] + ' <span class="text-secondary">@' + user["screen_name"] + '</span></h5>');
						$("#user_info").append('<h6 class="mt-0 text-secondary">User Description:</h6>');
						$("#user_info").append('<p>' + user["description"] === null ? "Not available" : user["description"] + '</p>');
					}
				});

				$("#logo").removeClass("fa-spin");
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
	getUnreviewedUserAnnotation();

	$("#firstunlabelled").click(getUnreviewedUserAnnotation);

	$("#revisit").click(function() {
		getUserAnnotation($("#page").val());
	});

	if (validate === 1)
	{
		$(document).keydown(function(e)
		{
			switch (e.key)
			{
				case "n":
					reviewAnnotation(-1);
					break;			
				case "y":
					reviewAnnotation(1)
					break;		
				case "j":
					reviewAnnotation(0);
					break;			
				case "h":
					$("#keyboard_shortcuts").toggle();
			}
		});
	}
});

