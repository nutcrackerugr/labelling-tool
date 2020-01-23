function login(e)
{
	var u = $("#username").val();
	var p = $("#password").val();
	
	var payload = {
		"username" : u,
		"password" : p
	};
	
	$.ajax({
		type: "POST",
		url: "/api/auth/login",
		data: JSON.stringify(payload),
		contentType:"application/json",
		dataType: "json",
		success: function(data)
		{
			localStorage.jwt_access = data.access_token;
			localStorage.jwt_refresh = data.refresh_token;
			window.location.replace("/tagging");
		},
		error: function(data)
		{
			console.log(data)
			if ($("#errormessage").length == 0)
				$("#cardbody").prepend('<div class="alert alert-danger" id="errormessage"><i class="fa fa-exclamation-triangle" aria-hidden="true"></i> Something went wrong :(<br />' + data.responseJSON["message"] + '</div>');
			else
				$("#errormessage").html('<i class="fa fa-exclamation-triangle" aria-hidden="true"></i> Something went wrong :(<br />' + data.responseJSON["message"] + '</div>')
		}
	});
	
	e.preventDefault();
	return false;
}

$(function()
{
	$("#loginbutton").click(login);
	$("#loginform").submit(login);
});
