var image_width = 509;
var image_height = 342;
var max_hour = 8759;
var img_base = '/output/all_hours/';

var legend_data = {
    names: [
        0,
        1,
        2,
        5,
        10,
        25,
        100,
        250,
        500,
        1000,
        "2000+"
    ],
    colors: [
        [
            0.0,
            0.0,
            0.0,
            1.0
        ],
        [
            0.5202411764705882,
            0.0,
            0.5869215686274509,
            1.0
        ],
        [
            0.0941117647058824,
            0.0,
            0.6549294117647059,
            1.0
        ],
        [
            0.0,
            0.3294352941176471,
            0.8667,
            1.0
        ],
        [
            0.0,
            0.6183098039215686,
            0.8117980392156863,
            1.0
        ],
        [
            0.0,
            0.6300803921568627,
            0.24050784313725487,
            1.0
        ],
        [
            0.11502745098039215,
            1.0,
            0.0,
            1.0
        ],
        [
            0.972535294117647,
            0.8548882352941177,
            0.0,
            1.0
        ],
        [
            1.0,
            0.36470588235294116,
            0.0,
            1.0
        ],
        [
            0.853621568627451,
            0.0,
            0.0,
            1.0
        ],
        [
            0.8,
            0.8,
            0.8,
            1.0
        ]
    ]
}

function image_scale () {
    var w_multiple = Math.floor($(window).innerWidth() / image_width);
    var h_multiple = Math.floor($(window).innerHeight() / image_height);
    var multiple = Math.min(w_multiple, h_multiple)
    return multiple ? multiple : 1;
}
function img_url (val) {
    return img_base + String($('#hour-selector').val()).padStart(4, '0') + '.png';
}
function update_slider_display (val) {
    var time = moment('Jan 1 00:00:00 2011', 'MMM DD hh:mm:ss YYYY').add(val, 'hours');
    $('#hour-selector-display').text(time.format('hh A ddd, MMM DD'));
}

$(document).ready(() => {
    var main_image = $('#main-image');
    var hour_selector = $('#hour-selector');
    var autoplay_button = $('#auto-play');
    var autoplay_interval = 0;
    var canvas = document.getElementById('legend');
    $(canvas).attr('width', image_scale() * image_width);
    var ctx = canvas.getContext('2d');

    $('#controls').css('width', image_scale() * image_width);

    ctx.textAlign = 'center';
    ctx.font = ' 12px Courier';

    var key_step = $(canvas).attr('width') / legend_data['names'].length;
    var key_offset = key_step / 2;
    _.each(_.zip(legend_data['names'], legend_data['colors']), (x, idx) => {
        var name = x[0];
        var color = _.map(x[1], (v) => { return Math.floor(v * 255); });
        ctx.fillStyle = `rgb( ${color[0]}, ${color[1]}, ${color[2]})`;
        ctx.fillRect(idx * key_step, 0, key_step, 20);
        ctx.fillStyle = 'black';
        ctx.fillText(String(name), key_offset + idx * key_step, 35);
    });
    ctx.textAlign = 'left';
    ctx.strokeText('tC:', 0, 35);
    ctx.fillText('tC:', 0, 35);

    main_image.attr('height', `${image_scale() * image_height}`);
    main_image.attr('width', `${image_scale() * image_width}`);

    hour_selector.on('input', () => {
        var val = $('#hour-selector').val();
        $('#main-image').attr('src', img_url(val));
        update_slider_display(val);
    });
    hour_selector.val(0);
    hour_selector.trigger('input');

    autoplay_button.click(() => {
        if (autoplay_interval) {
            clearInterval(autoplay_interval);
            autoplay_interval = 0;
            autoplay_button.removeClass('toggled');
        } else {
            autoplay_interval = setInterval(() => {
                var current_val = hour_selector.val();
                var new_val = parseInt(current_val) + 1;
                new_val = new_val > 168 ? 0 : new_val;
                hour_selector.val(new_val);
                hour_selector.trigger('input');
            }, 500)
            autoplay_button.addClass('toggled');
        }
    })
});
