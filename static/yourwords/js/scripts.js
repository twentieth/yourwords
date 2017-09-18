$(document).ready(function() {

$('.repeat-check-btn').width($('.read_sentence').width());
$('.end-gap').height($('footer.base').height()+50);


$('input[name="repeat-checked"]').click(function(){
	if($('.repeat-check').is(':checked'))
	{
		$('.repeat-check-btn').show()
	}
	else
	{
		$('.repeat-check-btn').hide()
	}
})



createRandomColouredList(['red', 'green', 'blue', 'teal', 'orange', 'purple'], 'pagination', true)





$('.modal-rating').find('header, .modal-close').click(function() {
	$('.modal-rating .modal-content').html('')
	$('.modal-rating').hide()
})





	$(".rand_polish").on('click', function() {
		getDataFromDatabase('field_polish_polish')
	});
	$(".field_polish_polish").on('click', function() {
		$(".field_polish_polish").css('cursor', 'default')
		$(".field_english_polish").fadeIn().css('cursor', 'pointer')
	})
	$(".field_english_polish").on('click', function() {
		$(".field_english_polish").css('cursor', 'default')
		if($('.field_sentence_polish').text() == '')
		{
			getDataFromDatabase('field_polish_polish')
		}
		else
		{
			$(".field_sentence_polish").fadeIn().css('cursor', 'pointer')
		}
	})
	$(".field_sentence_polish").on('click', function() {
		getDataFromDatabase('field_polish_polish')
	})

	//kliknięcie celem wylosowania słówka angielskiego
	$(".rand_english").on('click', function() {
		getDataFromDatabase('field_english_english')
	});
	$(".field_english_english").on('click', function() {
		$(".field_english_english").css('cursor', 'default')
		$(".field_polish_english").fadeIn().css('cursor', 'pointer')
	})
	$(".field_polish_english").on('click', function() {
		$(".field_polish_english").css('cursor', 'default')
		if($('.field_sentence_english').text() == '')
		{
			getDataFromDatabase('field_english_english')
		}
		else
		{
			$(".field_sentence_english").fadeIn().css('cursor', 'pointer')
		}
	})
	$(".field_sentence_english").on('click', function() {
		getDataFromDatabase('field_english_english')
	})
	
	
	$('.message_frame, .message_frame_js').on('click', function(){
		$('.message_frame, .message_frame_js').hide()
	});

	$('.menu1-btn').on('click', function(){
		$('.menu2, .menu3, .menusearch').hide()
		$('.menu1').fadeToggle(100)
	})
	$('.menu2-btn').on('click', function(){
		$('.menu1, .menu3, .menusearch').hide()
		$('.menu2').fadeToggle(100)
	})
	$('.menu3-btn').on('click', function(){
		$('.menu1, .menu2, .menusearch').hide()
		$('.menu3').fadeToggle(100)
	})
	$('.menusearch-btn').on('click', function(){
		$('.menu1, .menu2, .menu3').hide()
		$('.menusearch').fadeToggle(100)
		$('input[name="searched_text"]').focus()
	})
	

	$(document).click(function(event){ 
		if(!$(event.target).closest('.menu-container').length) {
		 if($('.menu-list').is(":visible")) {
			 $('.menu-list').fadeOut(100)
			}
		}
	})
	
	$('#search').on('submit', function(){
		if($('input[name="searched_text"]').val() == '')
		{
			showAndHideModal('warning', 'Nie podano frazy wyszukiwania.')
			return false
		}
	})

	$('#submit-btn-delete').on('click', function(e) {
		e.preventDefault()
		function delRecord()
		{
			$('#delete_record').submit()
		}
		showAndHideModalConfirm('Czy na pewno chcesz usunąć wybrany rekord?', delRecord, 'danger')
	})
	
	$('#listing_choice').click(function(e) {
		e.preventDefault()
		showAndHideModalFancybox('Powtórz słówka z wybranej listy', '/yourwords/listings/')
	})


$('.modal-rating-close, .modal-rating-header').click(function(){
	$('#rating-form').trigger('reset')
	$('#submit-rating-btn-ang').css({'visibility': 'hidden'})
})



$('button[type="reset"], input[type="reset"]').click(function(){
	$('input[type="text"], input[type="email"], input[type="password"], textarea').val('').removeClass('w3-border-red')
	$('.errors').hide()
});
$('input[type="text"], input[type="email"], input[type="password"], textarea').focus(function(){
	$(this).removeClass('w3-border-red')
})


$('#main_repeat_form').submit(function(){
	if(!$('input[name="main_repeat_manually"]').is(':disabled'))
	{
		var regex_number = /^[\d]+$/
		var val_number = $('input[name="main_repeat_manually"]').val().trim()

		if(!regex_number.test(val_number) || val_number < 1 || val_number > 99999)
		{
			showAndHideModal('warning', 'Wprowadzona wartość musi być liczbą w zakresie 1-99999.')
			return false
		}
	}
})


$('#main_repeat_form input[type="radio"]').click(function(){
	if($('input[value="manually"]').is(':checked'))
	{
		$('#main_repeat_form input[name="main_repeat_manually"]').prop('disabled', false).focus()
	}
	else
	{
		$('#main_repeat_form input[name="main_repeat_manually"]').prop('disabled', true)
		$('#main_repeat_form input[name="main_repeat_manually"]').val('')
	}
})

$('.disabled').click(function(e) {
	e.preventDefault()
})

$('#option_settings').click(function(e) {
	e.preventDefault()
	showAndHideModalFancybox('Wprowadź ustawienia użytkownika', '/accounts/settings/')
})

$('#change_language').click(function(e) {
	e.preventDefault()
	showAndHideModalFancybox('Wybierz język interfejsu', '/accounts/language/')
})








































});

