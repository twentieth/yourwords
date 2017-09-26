
	function createRandomColouredList(arr, ul_class, is_horizontal)
	{
		var c
		function setRandomInt(min, max)
		{
			min = Math.ceil(min)
			max = Math.floor(max)
			return Math.floor(Math.random()*(max-min+1))+min
		}
		$('.' + ul_class).css({
			'display': 'block',
			'list-style-type': 'none',
			'text-align': 'center',
			'padding': '0',
			'margin': '0 3px 0 5px'
		})
		if(is_horizontal)
		{
			$('.' + ul_class + ' li').css({
				'display': 'inline-block'
			})
		}
		$('.' + ul_class + ' li a').css({
			'text-decoration': 'none',
			'display': 'block',
			'padding': '10px',
			'color': 'black'
		})
		$('.material-icons').css({
			'padding': '0',
			'margin': '0'
		})
		$('.' + ul_class + ' li a').not('.disabled').mouseenter(function(){
			c = 'w3-hover-' + arr[setRandomInt(0, arr.length-1)]
			$(this).addClass(c)
		}).mouseleave(function(){
			$(this).removeClass(c)
		})
	}

	function showAndHideModal(type, content)
	{
		$('.modal-header').removeClass('w3-blue').removeClass('w3-orange').removeClass('w3-red')

		if(type == 'error')
		{
			$('.modal-header').addClass('w3-red')
		}
		if(type == 'warning')
		{
			$('.modal-header').addClass('w3-orange')
		}
		if(type == 'info')
		{
			$('.modal-header').addClass('w3-blue')
		}
		$('.modal-content').html(content)
		$('.modal-base').show()
		$('.modal-base').find('header, .modal-close').click(function() {
			$('.modal-content').html('')
			$('.modal-base').hide()
		})
	}

	function showAndHideModalConfirm(txt, fYes, type = '', onlyOk = false)
	{
		if (onlyOk) {
			$('.no').hide();
		}

		$('.modal-confirm').find('header').text(txt)
		if (type == 'danger') {
			$('.modal-confirm').find('header').addClass('w3-red')
			$('.modal-confirm').find('.yes').addClass('w3-red')

		}
		if (type == '') {
			$('.modal-confirm').find('header').addClass('w3-teal')
			$('.modal-confirm').find('.yes').addClass('w3-teal')
		}
		$('.modal-confirm').css({display: 'block'})
		$('.yes').click(function() {
			fYes()
		})
		$('.no').click(function () {
			hideModalConfirm()
		})
		$('.modal-confirm').find('header').click(function() {
			hideModalConfirm()
		})
	}
	function hideModalConfirm()
	{
		$('.modal-confirm').hide();
		$('.no').removeClass('w3-red, w3-teal');
		$('.modal-confirm').find('header').removeClass('w3-red, w3-teal').html('');
		$('.modal-confirm').find('.yes').removeClass('w3-teal, w3-red');
	}
	function showAndHideModalFancybox(header, view)
	{
		$('.modal-fancybox .modal-header #modal-fancybox-text').text(header)
		$('.modal-fancybox .modal-content').load(view)
		$('.modal-fancybox').show()
		$('.modal-fancybox .modal-header').click(function() {
			hideModalFancybox()
		})
	}
	function hideModalFancybox()
	{
		$('.modal-fancybox').hide()
		$('.modal-fancybox .modal-header #modal-fancybox-text').text('')
		$('.modal-fancybox .modal-content').html('')
	}

	function cleanFields()
	{
		$(".field_polish_polish, .field_english_polish, .field_english_english, .field_polish_english, .field_sentence_polish, .field_sentence_english").hide().text('')
		$('.rating').hide()
	}

	function clickExpandMenuButton(button_class, item_class)
	{
		$('.' + button_class).click(function(e) {
			e.preventDefault()
			if ($('.' + item_class).is(':visible')) {
				$('.' + item_class).slideUp('fast')
				$('.' + button_class).find('i').text('expand_more')
			} else {
				$('.' + item_class).slideDown('fast')
				$('.' + button_class).find('i').text('expand_less')
			}
		})
	}

	function excludeOption(enabledId, disabledId) {
	    var enabled = $('#' + enabledId);
	    var disabled = $('#' + disabledId);
	    enabled.click(function() {
	        if (disabled.is(':checked')) {
	            disabled.prop('checked', false);
	        }
	    });
	    disabled.click(function() {
	        if (enabled.is(':checked')) {
	            enabled.prop('checked', false);
	        }
	    });
	}