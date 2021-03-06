/*
 * jQuery Beauty Tips plugin
 * Version 0.7  (10/20/2008)
 * @requires jQuery v1.2+ (not fully tested on versions prior to 1.2.6)
 *
 * Dual licensed under the MIT and GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 *
 * No guarantees, warranties, or promises of any kind
 *
 */

/**
 * @name Beauty Tips
 * @type jQuery
 * @cat Plugins/tip
 * @return jQuery
 * @author Jeff Robbins - Lullabot - http://www.lullabot.com
 *
 * @credit Inspired by Karl Swedberg's ClueTip
 *    (http://plugins.learningjquery.com/cluetip/), which in turn was inspired
 *    by Cody Lindley's jTip (http://www.codylindley.com)
 *
 * @fileoverview
 * Beauty Tips is a jQuery tooltips plugin which uses the canvas drawing element
 * in the HTML5 spec in order to dynamically draw tooltip "talk bubbles" around
 * the descriptive help text associated with an item. This is in many ways
 * similar to Google Maps which both provides similar talk-bubbles and uses the
 * canvas element to draw them.
 *
 * The canvas element is supported in modern versions of FireFox, Safari, and
 * Opera. However, Internet Explorer needs a separate library called ExplorerCanvas
 * included on the page in order to support canvas drawing functions. ExplorerCanvas
 * was created by Google for use with their web apps and you can find it here:
 * http://excanvas.sourceforge.net/
 *
 * Beauty Tips was written to be simple to use and pretty. All of its options
 * are documented at the bottom of this file and defaults can be overwritten
 * globally for the entire page, or individually on each call.
 *
 * By default each tooltip will be positioned on the side of the target element
 * which has the most free space. This is affected by the scroll position and
 * size of the current window, so each Beauty Tip is redrawn each time it is
 * displayed. It may appear above an element at the bottom of the page, but when
 * the page is scrolled down (and the element is at the top of the page) it will
 * then appear below it. Additionally, positions can be forced or a preferred
 * order can be defined. See examples below.
 *
 * Usage
 * The function can be called in a number of ways.
 * $(selector).tip();
 * $(selector).tip('Content text');
 * $(selector).tip('Content text', {option1: value, option2: value});
 * $(selector).tip({option1: value, option2: value});
 *
 * Some examples:
 *
 * @example
 * $('[title]').tip();
 * This is probably the simplest example. It will go through the page finding
 * every element which has a title attribute and give it a Beauty Tips popup
 * which gets fired on hover.
 *
 * @example
 * $('h2').tip('I am an H2 element!', {trigger: 'click', positions: 'top'});
 * When any H2 element on the page is clicked on, a tip will appear above it.
 *
 * @example
 * $('a[href]').tip({
 *  titleSelector: "attr('href')",
 *  fill: 'red',
 *  cssStyles: {color: 'white', fontWeight: 'bold', width: 'auto'},
 *  width: 400,
 *  padding: 10,
 *  cornerRadius: 10,
 *  animate: true,
 *  spikeLength: 15,
 *  spikeGirth: 5,
 *  positions: ['left', 'right', 'bottom'],
 *  });
 * This will find all <a> tags and display a red baloon with bold white text
 * containing the href link. The box will be a variable width up to 400px with
 * rounded corners and will fade in and animate position toward the target
 * object when appearing. The script will try to position the box to the left,
 * then to the right, and finally it will place it on the bottom if it does not
 * fit elsewhere.
 *
 * @example
 * $('#my-table td[title]').tip({
 *  preShow: function() {
 *    $(this).data('origBG', $(this).css('background-color'));
 *    $(this).css('background-color', 'yellow');
 *  },
 *  postHide: function() {
 *    $(this).css('background-color', $(this).data('origBG'));
 *  }
 * });
 * Find every table cell within #mytable with a title attribute. Hilight the cell
 * yellow before displaying the BeautyTip. Restore it to its original background
 * when hiding/removing the BeautyTip.
 *
 * @example
 * $().tip.defaults.fill = 'rgba(102, 102, 255. .8)';
 * $(selector).tip();
 * All bubbles will be filled with a semi-transparent light-blue background
 * unless otherwise specified.
 *
 */
jQuery.fn.tip = function(content, options) {

  if (typeof content != 'string') {
    var contentSelect = true;
    options = content;
    content = false;
  }
  else {
    var contentSelect = false;
  }

  return this.each(function(index) {

    var opts = jQuery.extend(false, jQuery.fn.tip.defaults, options);

    // clean up the options
    opts.spikeLength = numb(opts.spikeLength);
    opts.spikeGirth = numb(opts.spikeGirth);
    opts.overlap = numb(opts.overlap);

    var turnOn = function () {

      if (typeof $(this).data('tip-box') == 'object') {
        // if there's already a popup, remove it before creating a new one.
        turnOff.apply(this);
      }

      // trigger preShow function
      opts.preShow.apply(this);

      if (contentSelect) {
        // bizarre, I know
        if (opts.killTitle) {
          // if we've killed the title attribute, it's been stored in 'tip-xTitle' so get it..
          $(this).attr('title', $(this).attr('tip-xTitle'));
        }
        // then evaluate the selector... title is now in place
        content = eval('$(this).' + opts.titleSelector);
        if (opts.killTitle) {
          // now remove the title again, so we don't get double tips
          $(this).removeAttr('title');
        }
      }

      var offsetParent = $(this).offsetParent();
      var pos = $(this).tipPosition();
      var top = numb(pos.top) + numb($(this).css('margin-top')); // IE can return 'auto' for margins
      var left = numb(pos.left) + numb($(this).css('margin-left'));
      var width = $(this).outerWidth();
      var height = $(this).outerHeight();

      // get the dimensions of the text box
      var $text = $('<div class="tip-content"></div>').append(content).css({padding: opts.padding + 'px', position: 'absolute', width: opts.width + 'px', zIndex: opts.textzIndex}).css(opts.cssStyles);
      var $box = $('<div class="tip-wrapper"></div>').append($text).addClass(opts.cssClass).css({position: 'absolute', width: opts.width + 'px'}).appendTo(offsetParent);

      $(this).data('tip-box', $box);

      // see if the text box will fit in the various positions
      var scrollTop = numb($(document).scrollTop());
      var scrollLeft = numb($(document).scrollLeft());
      var docWidth = numb($(window).width());
      var docHeight = numb($(window).height());
      var winRight = scrollLeft + docWidth;
      var winBottom = scrollTop + docHeight;
      var space = new Object();
      space.top = $(this).offset().top - scrollTop;
      space.bottom = docHeight - (($(this).offset().top + height) - scrollTop);
      space.left = $(this).offset().left - scrollLeft;
      space.right = docWidth - (($(this).offset().left + width) - scrollLeft);
      var textOutHeight = numb($text.outerHeight());
      var textOutWidth = numb($text.outerWidth());
      if (opts.positions.constructor == String) {
        opts.positions = opts.positions.replace(/ /, '').split(',');
      }
      if (opts.positions[0] == 'most') {
        // figure out which is the largest
        var position = 'top'; // prime the pump
        for (var pig in space) { // pigs in space!
          position = space[pig] > space[position] ? pig : position;
        }
      }
      else {
        for (var x in opts.positions) {
          var position = opts.positions[x];
          if ((position == 'left' || position == 'right') && space[position] > textOutWidth + opts.spikeLength) {
            break;
          }
          else if ((position == 'top' || position == 'bottom') && space[position] > textOutHeight + opts.spikeLength) {
            break;
          }
        }
      }

      var horiz = left + ((width - textOutWidth)/2);
      var vert = top + ((height - textOutHeight)/2);
      var animDist = opts.animate ? numb(opts.distance) : 0;
      var points = new Array();
      var textTop, textLeft, textRight, textBottom, textTopSpace, textBottomSpace, textLeftSpace, textRightSpace, crossPoint, textCenter;

      // Yes, yes, this next bit really could use to be condensed
      // each switch case is basically doing the same thing in slightly different ways
      switch(position) {
        case 'top':
          // spike on bottom
          $text.css('margin-bottom', opts.spikeLength + 'px');
          $box.css({top: (top - $text.outerHeight(true) - animDist) + opts.overlap, left: horiz});
          // move text left/right if extends out of window
          textRightSpace = (winRight - opts.windowMargin) - ($text.offset().left + $text.outerWidth(true));
          var xShift = 0;
          if (textRightSpace < 0) {
            // shift it left
            $box.css('left', (numb($box.css('left')) + textRightSpace) + 'px');
            xShift -= textRightSpace;
          }
          // we test left space second to ensure that left of box is visible
          textLeftSpace = ($text.offset().left + numb($text.css('margin-left'))) - (scrollLeft + opts.windowMargin);
          if (textLeftSpace < 0) {
            // shift it right
            $box.css('left', (numb($box.css('left')) - textLeftSpace) + 'px');
            xShift += textLeftSpace;
          }
          textTop = $text.tipPosition().top + numb($text.css('margin-top'));
          textLeft = $text.tipPosition().left + numb($text.css('margin-left'));
          textRight = textLeft + $text.outerWidth();
          textBottom = textTop + $text.outerHeight();
          textCenter = {x: textLeft + ($text.outerWidth()/2), y: textTop + ($text.outerHeight()/2)};
          // points[points.length] = {x: x, y: y};
          points[points.length] = spikePoint = {y: textBottom + opts.spikeLength, x: ((textRight-textLeft)/2) + xShift, type: 'spike'};
          crossPoint = findIntersectX(spikePoint.x, spikePoint.y, textCenter.x, textCenter.y, textBottom);
          // make sure that the crossPoint is not outside of text box boundaries
          crossPoint.x = crossPoint.x < textLeft + opts.spikeGirth/2 + opts.cornerRadius ? textLeft + opts.spikeGirth/2 + opts.cornerRadius : crossPoint.x;
          crossPoint.x =  crossPoint.x > (textRight - opts.spikeGirth/2) - opts.cornerRadius ? (textRight - opts.spikeGirth/2) - opts.CornerRadius : crossPoint.x;
          points[points.length] = {x: crossPoint.x - (opts.spikeGirth/2), y: textBottom, type: 'join'};
          points[points.length] = {x: textLeft, y: textBottom, type: 'corner'};  // left bottom corner
          points[points.length] = {x: textLeft, y: textTop, type: 'corner'};     // left top corner
          points[points.length] = {x: textRight, y: textTop, type: 'corner'};    // right top corner
          points[points.length] = {x: textRight, y: textBottom, type: 'corner'}; // right bottom corner
          points[points.length] = {x: crossPoint.x + (opts.spikeGirth/2), y: textBottom, type: 'join'};
          points[points.length] = spikePoint;
          break;
        case 'left':
          // spike on right
          $text.css('margin-right', opts.spikeLength + 'px');
          $box.css({top: vert + 'px', left: ((left - $text.outerWidth(true) - animDist) + opts.overlap) + 'px'});
          // move text up/down if extends out of window
          textBottomSpace = (winBottom - opts.windowMargin) - ($text.offset().top + $text.outerHeight(true));
          var yShift = 0;
          if (textBottomSpace < 0) {
            // shift it up
            $box.css('top', (numb($box.css('top')) + textBottomSpace) + 'px');
            yShift -= textBottomSpace;
          }
          // we ensure top space second to ensure that top of box is visible
          textTopSpace = ($text.offset().top + numb($text.css('margin-top'))) - (scrollTop + opts.windowMargin);
          if (textTopSpace < 0) {
            // shift it down
            $box.css('top', (numb($box.css('top')) - textTopSpace) + 'px');
            yShift += textTopSpace;
          }
          textTop = $text.tipPosition().top + numb($text.css('margin-top'));
          textLeft = $text.tipPosition().left + numb($text.css('margin-left'));
          textRight = textLeft + $text.outerWidth();
          textBottom = textTop + $text.outerHeight();
          textCenter = {x: textLeft + ($text.outerWidth()/2), y: textTop + ($text.outerHeight()/2)};
          points[points.length] = spikePoint = {x: textRight + opts.spikeLength, y: ((textBottom-textTop)/2) + yShift, type: 'spike'};
          crossPoint = findIntersectY(spikePoint.x, spikePoint.y, textCenter.x, textCenter.y, textRight);
          // make sure that the crossPoint is not outside of text box boundaries
          crossPoint.y = crossPoint.y < textTop + opts.spikeGirth/2 + opts.cornerRadius ? textTop + opts.spikeGirth/2 + opts.cornerRadius : crossPoint.y;
          crossPoint.y =  crossPoint.y > (textBottom - opts.spikeGirth/2) - opts.cornerRadius ? (textBottom - opts.spikeGirth/2) - opts.cornerRadius : crossPoint.y;
          points[points.length] = {x: textRight, y: crossPoint.y + opts.spikeGirth/2, type: 'join'};
          points[points.length] = {x: textRight, y: textBottom, type: 'corner'}; // right bottom corner
          points[points.length] = {x: textLeft, y: textBottom, type: 'corner'};  // left bottom corner
          points[points.length] = {x: textLeft, y: textTop, type: 'corner'};     // left top corner
          points[points.length] = {x: textRight, y: textTop, type: 'corner'};    // right top corner
          points[points.length] = {x: textRight, y: crossPoint.y - opts.spikeGirth/2, type: 'join'};
          points[points.length] = spikePoint;
          break;
        case 'bottom':
          // spike on top
          $text.css('margin-top', opts.spikeLength + 'px');
          $box.css({top: (top + height + animDist) - opts.overlap, left: horiz});
          // move text up/down if extends out of window
          textRightSpace = (winRight - opts.windowMargin) - ($text.offset().left + $text.outerWidth(true));
          var xShift = 0;
          if (textRightSpace < 0) {
            // shift it left
            $box.css('left', (numb($box.css('left')) + textRightSpace) + 'px');
            xShift -= textRightSpace;
          }
          // we ensure left space second to ensure that left of box is visible
          textLeftSpace = ($text.offset().left + numb($text.css('margin-left')))  - (scrollLeft + opts.windowMargin);
          if (textLeftSpace < 0) {
            // shift it right
            $box.css('left', (numb($box.css('left')) - textLeftSpace) + 'px');
            xShift += textLeftSpace;
          }
          textTop = $text.tipPosition().top + numb($text.css('margin-top'));
          textLeft = $text.tipPosition().left + numb($text.css('margin-left'));
          textRight = textLeft + $text.outerWidth();
          textBottom = textTop + $text.outerHeight();
          textCenter = {x: textLeft + ($text.outerWidth()/2), y: textTop + ($text.outerHeight()/2)};
          points[points.length] = spikePoint = {x: ((textRight-textLeft)/2) + xShift, y: 0, type: 'spike'};
          crossPoint = findIntersectX(spikePoint.x, spikePoint.y, textCenter.x, textCenter.y, textTop);
          // make sure that the crossPoint is not outside of text box boundaries
          crossPoint.x = crossPoint.x < textLeft + opts.spikeGirth/2 + opts.cornerRadius ? textLeft + opts.spikeGirth/2 + opts.cornerRadius : crossPoint.x;
          crossPoint.x =  crossPoint.x > (textRight - opts.spikeGirth/2) - opts.cornerRadius ? (textRight - opts.spikeGirth/2) - opts.cornerRadius : crossPoint.x;
          points[points.length] = {x: crossPoint.x + opts.spikeGirth/2, y: textTop, type: 'join'};
          points[points.length] = {x: textRight, y: textTop, type: 'corner'};    // right top corner
          points[points.length] = {x: textRight, y: textBottom, type: 'corner'}; // right bottom corner
          points[points.length] = {x: textLeft, y: textBottom, type: 'corner'};  // left bottom corner
          points[points.length] = {x: textLeft, y: textTop, type: 'corner'};     // left top corner
          points[points.length] = {x: crossPoint.x - (opts.spikeGirth/2), y: textTop, type: 'join'};
          points[points.length] = spikePoint;
          break;
        case 'right':
          // spike on left
          $text.css('margin-left', (opts.spikeLength + 'px'));
          $box.css({top: vert + 'px', left: ((left + width + animDist) - opts.overlap) + 'px'});
          // move text up/down if extends out of window
          textBottomSpace = (winBottom - opts.windowMargin) - ($text.offset().top + $text.outerHeight(true));
          var yShift = 0;
          if (textBottomSpace < 0) {
            // shift it up
            $box.css('top', (numb($box.css('top')) + textBottomSpace) + 'px');
            yShift -= textBottomSpace;
          }
          // we ensure top space second to ensure that top of box is visible
          textTopSpace = ($text.offset().top + numb($text.css('margin-top'))) - (scrollTop + opts.windowMargin);
          if (textTopSpace < 0) {
            // shift it down
            $box.css('top', (numb($box.css('top')) - textTopSpace) + 'px');
            yShift += textTopSpace;
          }
          textTop = $text.tipPosition().top + numb($text.css('margin-top'));
          textLeft = $text.tipPosition().left + numb($text.css('margin-left'));
          textRight = textLeft + $text.outerWidth();
          textBottom = textTop + $text.outerHeight();
          textCenter = {x: textLeft + ($text.outerWidth()/2), y: textTop + ($text.outerHeight()/2)};
          points[points.length] = spikePoint = {x: 0, y: ((textBottom-textTop)/2) + yShift, type: 'spike'};
          crossPoint = findIntersectY(spikePoint.x, spikePoint.y, textCenter.x, textCenter.y, textLeft);
          // make sure that the crossPoint is not outside of text box boundaries
          crossPoint.y = crossPoint.y < textTop + opts.spikeGirth/2 + opts.cornerRadius ? textTop + opts.spikeGirth/2 + opts.cornerRadius : crossPoint.y;
          crossPoint.y =  crossPoint.y > (textBottom - opts.spikeGirth/2) - opts.cornerRadius ? (textBottom - opts.spikeGirth/2) - opts.cornerRadius : crossPoint.y;
          points[points.length] = {x: textLeft, y: crossPoint.y - opts.spikeGirth/2, type: 'join'};
          points[points.length] = {x: textLeft, y: textTop, type: 'corner'};     // left top corner
          points[points.length] = {x: textRight, y: textTop, type: 'corner'};    // right top corner
          points[points.length] = {x: textRight, y: textBottom, type: 'corner'}; // right bottom corner
          points[points.length] = {x: textLeft, y: textBottom, type: 'corner'};  // left bottom corner
          points[points.length] = {x: textLeft, y: crossPoint.y + opts.spikeGirth/2, type: 'join'};
          points[points.length] = spikePoint;
          break;
      } // </ switch >

      var canvas = $('<canvas width="'+ (numb($text.outerWidth(true)) + opts.strokeWidth*2) +'" height="'+ (numb($text.outerHeight(true)) + opts.strokeWidth*2) +'"></canvas>').appendTo($box).css({position: 'absolute', top: $text.tipPosition().top, left: $text.tipPosition().left, zIndex: opts.boxzIndex}).get(0);

      // if excanvas is set up, we need to initialize the new canvas element
      if (typeof G_vmlCanvasManager != 'undefined') {
        canvas = G_vmlCanvasManager.initElement(canvas);
      }

      if (opts.cornerRadius > 0) {
        // round the corners!
        var newPoints = new Array();
        var newPoint;
        for (var i=0; i<points.length; i++) {
          if (points[i].type == 'corner') {
            // create two new arc points
            // find point between this and previous (using modulo in case of ending)
            newPoint = betweenPoint(points[i], points[(i-1)%points.length], opts.cornerRadius);
            newPoint.type = 'arcStart';
            newPoints[newPoints.length] = newPoint;
            // the original corner point
            newPoints[newPoints.length] = points[i];
            // find point between this and next
            newPoint = betweenPoint(points[i], points[(i+1)%points.length], opts.cornerRadius);
            newPoint.type = 'arcEnd';
            newPoints[newPoints.length] = newPoint;
          }
          else {
            newPoints[newPoints.length] = points[i];
          }
        }
        // overwrite points with new version
        points = newPoints;

      }

      var ctx = canvas.getContext("2d");
      drawIt.apply(ctx, [points]);
      ctx.fillStyle = opts.fill;
      if (opts.shadow) {
        ctx.shadowOffsetX = 2;
        ctx.shadowOffsetY = 2;
        ctx.shadowBlur = 5;
        ctx.shadowColor =  opts.shadowColor;
      }
      ctx.closePath();
      ctx.fill();
      if (opts.strokeWidth > 0) {
        ctx.lineWidth = opts.strokeWidth;
        ctx.strokeStyle = opts.strokeStyle;
        ctx.beginPath();
        drawIt.apply(ctx, [points]);
        ctx.closePath();
        ctx.stroke();
      }

      if (opts.animate) {
        $box.css({opacity: 0.1});
      }

      $box.css({visibility: 'visible'});

      if (opts.overlay) {
        var overlay = $('<div class="tip-overlay"></div>').css({
            position: 'absolute',
            backgroundColor: 'blue',
            top: top,
            left: left,
            width: width,
            height: height,
            opacity: '.2'
          }).appendTo(offsetParent);
        $(this).data('overlay', overlay);
      }

      var animParams = {opacity: 1};
      if (opts.animate) {
        switch (position) {
          case 'top':
            animParams.top = $box.tipPosition().top + opts.distance;
            break;
          case 'left':
            animParams.left = $box.tipPosition().left + opts.distance;
            break;
          case 'bottom':
            animParams.top = $box.tipPosition().top - opts.distance;
            break;
          case 'right':
            animParams.left = $box.tipPosition().left - opts.distance;
            break;
        }
        $box.animate(animParams, {duration: opts.speed, easing: opts.easing});
      }

      // trigger postShow function
      opts.postShow.apply(this);


    } // </ turnOn() >

    var turnOff = function() {

      // trigger preHide function
      opts.preHide.apply(this);

      var box = $(this).data('tip-box');
      var overlay = $(this).data('tip-overlay');
      if (typeof box == 'object') {
        $(box).remove();
        $(this).removeData('tip-box');
      }
      if (typeof overlay == 'object') {
        $(overlay).remove();
        $(this).removeData('tip-overlay');
      }

      // trigger postHide function
      opts.postHide.apply(this);

    } // </ turnOff() >

    var refresh = function() {
      turnOff.apply(this);
      turnOn.apply(this);
    }

    /**
     * This is sort of the "starting spot" for the this.each()
     * These are sort of the init functions to handle the call
     */

    if (opts.killTitle) {
      $(this).find('[title]').andSelf().each(function() {
        $(this).attr('tip-xTitle', $(this).attr('title')).removeAttr('title');
      });
    }
    if (typeof opts.trigger == 'string') {
      opts.trigger = [opts.trigger];
    }
    if (opts.trigger[0] == 'hover') {
      $(this).hover(
        function() {
          turnOn.apply(this);
        },
        function() {
          turnOff.apply(this);
        }
      );
    }
    else if (opts.trigger[0] == 'now') {
      var box = $(this).data('tip-box');
      if (typeof box == 'object') {
        turnOff.apply(this);
      }
      else {
        turnOn.apply(this);
      }
    }
    else if (opts.trigger.length > 1 && opts.trigger[0] != opts.trigger[1]) {
      $(this)
        .bind(opts.trigger[0], function() {
          turnOn.apply(this);
        })
        .bind(opts.trigger[1], function() {
          turnOff.apply(this);
        });
    }
    else {
      // toggle using the same event
      $(this).bind(opts.trigger[0], function() {
        if (typeof this.triggerToggle == 'undefined') {
          this.triggerToggle = false;
        }
        this.triggerToggle = !this.triggerToggle;
        if (this.triggerToggle) {
          turnOn.apply(this);
        }
        else {
          turnOff.apply(this);
        }
      });
    }
  }); // </ this.each() >


  function drawIt(points) {
    this.moveTo(points[0].x, points[0].y);
    for (i=1;i<points.length;i++) {
      if (points[i-1].type == 'arcStart') {
        // if we're creating a rounded corner
        //ctx.arc(round5(points[i].x), round5(points[i].y), points[i].startAngle, points[i].endAngle, opts.cornerRadius, false);
        this.quadraticCurveTo(round5(points[i].x), round5(points[i].y), round5(points[(i+1)%points.length].x), round5(points[(i+1)%points.length].y));
        i++;
        //ctx.moveTo(round5(points[i].x), round5(points[i].y));
      }
      else {
        this.lineTo(round5(points[i].x), round5(points[i].y));
      }
    }
  }

  /**
   * Round to the nearest .5 pixel to avoid antialiasing
   * http://developer.mozilla.org/en/Canvas_tutorial/Applying_styles_and_colors
   */
  function round5(num) {
    return Math.round(num - .5) + .5;
  }

  /**
   * Ensure that a number is a number... or zero
   */
  function numb(num) {
    return parseInt(num) || 0;
  }

  /**
   * Given two points, find a point which is dist pixels from point1 on a line to point2
   */
  function betweenPoint(point1, point2, dist) {
    // figure out if we're horizontal or vertical
    var y, x;
    if (point1.x == point2.x) {
      // vertical
      y = point1.y < point2.y ? point1.y + dist : point1.y - dist;
      return {x: point1.x, y: y};
    }
    else if (point1.y == point2.y) {
      // horizontal
      x = point1.x < point2.x ? point1.x + dist : point1.x - dist;
      return {x:x, y: point1.y};
    }
  }

  function centerPoint(arcStart, corner, arcEnd) {
    var x = corner.x == arcStart.x ? arcEnd.x : arcStart.x;
    var y = corner.y == arcStart.y ? arcEnd.y : arcStart.y;
    var startAngle, endAngle;
    if (arcStart.x < arcEnd.x) {
      if (arcStart.y > arcEnd.y) {
        // arc is on upper left
        startAngle = (Math.PI/180)*180;
        endAngle = (Math.PI/180)*90;
      }
      else {
        // arc is on upper right
        startAngle = (Math.PI/180)*90;
        endAngle = 0;
      }
    }
    else {
      if (arcStart.y > arcEnd.y) {
        // arc is on lower left
        startAngle = (Math.PI/180)*270;
        endAngle = (Math.PI/180)*180;
      }
      else {
        // arc is on lower right
        startAngle = 0;
        endAngle = (Math.PI/180)*270;
      }
    }
    return {x: x, y: y, type: 'center', startAngle: startAngle, endAngle: endAngle};
  }

  /**
   * Find the intersection point of two lines, each defined by two points
   * arguments are x1, y1 and x2, y2 for r1 (line 1) and r2 (line 2)
   * It's like an algebra party!!!
   */
  function findIntersect(r1x1, r1y1, r1x2, r1y2, r2x1, r2y1, r2x2, r2y2) {

    if (r2x1 == r2x2) {
      return findIntersectY(r1x1, r1y1, r1x2, r1y2, r2x1);
    }
    if (r2y1 == r2y2) {
      return findIntersectX(r1x1, r1y1, r1x2, r1y2, r2y1);
    }

    // m = (y1 - y2) / (x1 - x2)  // <-- how to find the slope
    // y = mx + b                 // the 'classic' linear equation
    // b = y - mx                 // how to find b (the y-intersect)
    // x = (y - b)/m              // how to find x
    var r1m = (r1y1 - r1y2) / (r1x1 - r1x2);
    var r1b = r1y1 - (r1m * r1x1);
    var r2m = (r2y1 - r2y2) / (r2x1 - r2x2);
    var r2b = r2y1 - (r2m * r2x1);

    var x = (r2b - r1b) / (r1m - r2m);
	  var y = r1m * x + r1b;

	  return {x: x, y: y};
  }

  /**
   * Find the y intersection point of a line and given x vertical
   */
  function findIntersectY(r1x1, r1y1, r1x2, r1y2, x) {
    if (r1y1 == r1y2) {
      return {x: x, y: r1y1};
    }
    var r1m = (r1y1 - r1y2) / (r1x1 - r1x2);
    var r1b = r1y1 - (r1m * r1x1);

    var y = r1m * x + r1b;

    return {x: x, y: y};
  }

  /**
   * Find the x intersection point of a line and given y horizontal
   */
  function findIntersectX(r1x1, r1y1, r1x2, r1y2, y) {
    if (r1x1 == r1x2) {
      return {x: r1x1, y: y};
    }
    var r1m = (r1y1 - r1y2) / (r1x1 - r1x2);
    var r1b = r1y1 - (r1m * r1x1);

    // y = mx + b     // your old friend, linear equation
    // x = (y - b)/m  // linear equation solved for x
    var x = (y - r1b) / r1m;

    return {x: x, y: y};

  }

}; // </ jQuery.fn.tip() >

/**
 * jQuery's compat.js (used in Drupal's jQuery upgrade module, overrides the $().position() function
 *  this is a copy of that function to allow the plugin to work when compat.js is present
 *  once compat.js is fixed to not override existing functions, this function can be removed
 *  and .tipPosion() can be replaced with .position() above...
 */
jQuery.fn.tipPosition = function() {

  function num(elem, prop) {
    return elem[0] && parseInt( jQuery.curCSS(elem[0], prop, true), 10 ) || 0;
  }

  var left = 0, top = 0, results;

  if ( this[0] ) {
    // Get *real* offsetParent
    var offsetParent = this.offsetParent(),

    // Get correct offsets
    offset       = this.offset(),
    parentOffset = /^body|html$/i.test(offsetParent[0].tagName) ? { top: 0, left: 0 } : offsetParent.offset();

    // Sutipract element margins
    // note: when an element has margin: auto the offsetLeft and marginLeft
    // are the same in Safari causing offset.left to incorrectly be 0
    offset.top  -= num( this, 'marginTop' );
    offset.left -= num( this, 'marginLeft' );

    // Add offsetParent borders
    parentOffset.top  += num( offsetParent, 'borderTopWidth' );
    parentOffset.left += num( offsetParent, 'borderLeftWidth' );

    // Sutipract the two offsets
    results = {
      top:  offset.top  - parentOffset.top,
      left: offset.left - parentOffset.left
    };
  }

  return results;
}; // </ jQuery.fn.tipPosition() >


/**
 * Defaults for the beauty tips
 *
 * Note this is a variable definition and not a function. So defaults can be
 * written for an entire page by simply redefining attributes like so:
 *
 *   jQuery.fn.tip.defaults.width = 400;
 *
 * This would make all Beauty Tips boxes 400px wide.
 *
 * Each of these options may also be overridden during
 *
 * Can be overriden globally or at time of call.
 *
 */
jQuery.fn.tip.defaults = {
  trigger:         'hover',                // trigger to show/hide tip
                                           // use [on, off] to define separate on/off triggers
                                           // also use space character to allow multiple events to trigger
                                           // examples:
                                           //   ['focus', 'blur'] // focus displays, blur hides
                                           //   'dblclick'        // dblclick toggles on/off
                                           //   ['focus mouseover', 'blur mouseout']
                                           //   'now'             // shows/hides tip without event

  width:            200,                   // width (in px) of tooltip box
                                           //   when combined with cssStyles: {width: 'auto'}, this becomes a max-width for the text
  padding:          10,                    // padding for content (get more fine grained with cssStyles)
  spikeGirth:       10,                    // width of spike
  spikeLength:      15,                    // length of spike
  overlap:          0,                     // spike overlap (px) onto target
  overlay:          false,                 // display overlay on target (use CSS to style) -- BUGGY!
  killTitle:        true,                  // kill title tag to avoid double tooltips

  textzIndex:       9999,                  // z-index for the text
  boxzIndex:        9990,                  // z-index for the "talk" box (should always be less than textzIndex)
  positions:        ['most'],              // preference of positions for tip (will use first with available space)
                                           // possible values 'top', 'bottom', 'left', 'right' as an array in order of
                                           // preference. Last value will be used if others don't have enough space.

                                           // or use 'most' to use the area with the most space
  fill:             "#EBE0EF",  // fill color for the tooltip box
  windowMargin:     10,                        // space (px) to leave between text box and browser edge

  strokeWidth:      1,                         // width of stroke around box, **set to 0 for no stroke**
  strokeStyle:      "#000",                    // color/alpha of stroke

  cornerRadius:     5,                         // radius of corners (px), set to 0 for square corners

  shadow:           false,                     // use drop shadow? (only displays in Safari and FF 3.1)
  shadowOffsetX:    2,                         // shadow offset x (px)
  shadowOffsetY:    2,                         // shadow offset y (px)
  shadowBlur:       3,                         // shadow blur (px)
  shadowColor:      "#000",                    // shadow color/alpha

  animate:          false,                     // animate show/hide of box - EXPERIMENTAL (buggy in IE)
  distance:         15,                        // distance of animation movement (px)
  easing:           'swing',                   // animation easing
  speed:            200,                       // speed (ms) of animation

  cssClass:         '',                        // CSS class to add to the box wrapper div
  cssStyles:        {},                        // styles to add the text box
                                               //   example: {fontFamily: 'Georgia, Times, serif', fontWeight: 'bold'}

  titleSelector:    "attr('title')",           // if there is no content argument, use this selector to retrieve the title

  preShow:          function(){return;},       // function to run before popup is built and displayed
  postShow:         function(){return;},       // function to run after popup is built and displayed
  preHide:          function(){return;},       // function to run before popup is removed
  postHide:         function(){return;}        // function to run after popup is removed

}; // </ jQuery.tip.defaults >
