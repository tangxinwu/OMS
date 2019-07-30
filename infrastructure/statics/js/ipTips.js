/**
 * å½“å‰æ–‡ä»¶ç‰ˆæœ¬ï¼šv0.1
 * ä¸€æ¬¾ç®€å•çš„é¼ æ ‡æç¤ºjsåº“
 * ============================================
 * é¡¹ç›®åœ°å€ï¼šhttps://github.com/ALNY-AC/mTips
 * ä½œè€…ï¼šè§ä¸¤å°å„¿ä¾¿æ—¥
 * ä½œè€…åœ°å€ï¼šhttps://github.com/ALNY-AC
 * ============================================
 *
 * */

var mTips = {
	c: {
		//é…ç½®é¡¹
		x: 10, //xåç§»é‡,ç›¸å¯¹äºŽé¼ æ ‡
		y: 10, //yåç§»é‡,ç›¸å¯¹äºŽé¼ æ ‡

		style: {
			'position': 'fixed',
			'padding': '8px 12px',
			'color': '#fff',
			'border-radius': '5px',
			'font-family': "å¾®è½¯é›…é»‘",
			'z-index': '999',
			'display': 'inline',
			'font-size': '14px',
			'background-color': 'rgba(0, 0, 0, 0.5)',
			'color': '#fff'

		}
	},
	//showæ–¹æ³•ï¼Œç”¨äºŽæ˜¾ç¤ºæç¤º

	s: function(text, a, b) {
		var style;
		var fun;

		if(typeof(a) == 'string') {
			style = a;
			fun = b;
		} else if(typeof(a) == 'function') {
			style = b;
			fun = a;
		}

		if(style == 'undefined' || style == null) {
			style = 'default';
		}

		var doc = $('<div></div>').addClass('mTips mTips-' + style).html(text).appendTo('body');
		if(doc.css('z-index') !== '999') {
			doc.css(this.c.style);
		}

		$(document).on('mousemove', function(e) {
			$(".mTips").offset({
				top: e.pageY + mTips.c.x,
				left: e.pageX + mTips.c.y
			})
		});

		if(fun != null && typeof(fun) != 'undefined') {
			fun();
		}

	},

	//hideæ–¹æ³•ï¼Œç”¨äºŽéšè—å’Œåˆ é™¤æç¤º
	h: function(fun) {

		$('.mTips').remove();
		if(fun != 'undefined' && fun != null) {
			fun();
		}

	},

	//ç”¨äºŽç»™ç›¸å…³å±žæ€§æ·»åŠ æç¤ºåŠŸèƒ½
	m: function() {

		$(document).on('mouseenter', '[data-mtpis]', function(e) {
			mTips.s($(this).attr('data-mtpis'), $(this).attr('data-mtpis-style'));
		});

		$(document).on('mouseleave', '[data-mtpis]', function(e) {
			mTips.h();
		});

	}

}
mTips.m(); //é€šè¿‡æ­¤å‡½æ•°æ¿€æ´»æ‰€æœ‰çš„