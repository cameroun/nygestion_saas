
odoo.define('theme_impacto.data_slider', function(require){
  "use strict";
    
  //  var animation = require('web_editor.snippets.animation');
   var sAnimation = require('website.content.snippets.animation');
    
    var defaults = {
        lazyLoad: 'ondemand',
        slidesToShow: 4,
        slidesToScroll: 1,
        dots: true,
        infinite: true,
        speed: 500,
        arrows: true,
        autoplay: true,
        adaptiveHeight: false,
        variableWidth: false,
        autoplaySpeed: 3000,
        data_model: 'product.template',
        data_domain: [['website_published', '=', true]],
        data_image_field: 'image',
        data_name_field: 'display_name',
        data_name_price: 'product.price',
        data_title: 'Our Products',
        data_title_tag: 'h2',
        data_title_class: 'text-center',
        data_uri_field: 'website_url',
        data_container_width: '90%',
        data_limit: 10,
    };
    
    sAnimation.registry.data_slider = sAnimation.Class.extend({
        selector: ".o_data_slider",
        
        slickSetOption: function(event, key, val) {
            switch (val) {
                case 'true':
                    val = true;
                    break;
                case 'false':
                    val = false;
                    break;
                case undefined:
                    return;
            }
            if (typeof val === 'object') {
                return;
            }
            this.$slick.slick('slickSetOption', key, val, true);
        },
        
        // It loops parses JSON records and calls _handleRecord on each
        handleRecords: function(records) {
            _.each(JSON.parse(records), $.proxy(this._handleRecord, this)); 
        },
        
        // Accepts a record object and appends to slick
        _handleRecord: function(record) {
            var $img = $('<img>');
            var $div = $('<div class="thumbnail">');
            var $href = $('<a>').attr('href', record[this.uriField]);
            var $title = $('<h5 class="f-weight-400 mb-0">').text(record[this.fields[0]]);
            var $caption = $('<div class="caption">').append($title);
            $div.append($href);
            var imgUri = this.baseUri + '/' + record.id + '/' + this.imageField;

            $img.attr('src', imgUri);
            $href.append($img).append($caption);
            this.$slick.append($div); 
            if(this.$slick.hasClass('o_slick_container')){
                this.$slick.slick('slickAdd', $div);
                this.$slick.slick('slickGoTo', 0);
            }
        },
        
        start: function() {
            this.widgetOptions = this.$target.data('options');
            var newpost = this.$target.data('fullview');
            this.$slick = $('<div class="o_slick_container oe_structure">');
            if(newpost){
                 this.$slick = $('<div class="product-list clearfix">');
            }

           
            this.$target.find('.add-product').html(this.$slick);
            
            if (!this.widgetOptions) {
                this.widgetOptions = defaults;
                this.$target.attr('data-options', JSON.stringify(this.widgetOptions));
            }
            
            if(!newpost){
                this.$slick.slick(this.widgetOptions);            
                this.$slick.on('set-option', $.proxy(this.slickSetOption, this));
            }
                
            this.model = this.widgetOptions.data_model;
            this.domain = this.widgetOptions.data_domain;
            this.imageField = this.widgetOptions.data_image_field;
            this.dataLimit = this.widgetOptions.data_limit;
            this.nameField = this.widgetOptions.data_name_field;
            this.titleTag = this.widgetOptions.data_title_tag;
            this.titleStr = this.widgetOptions.data_title;
            this.titleClass = this.widgetOptions.data_title_class;
            this.uriField = this.widgetOptions.data_uri_field;
            this.baseUri = '/web/image/' + this.model;
            this.fields = [this.nameField, this.uriField, 'id'];
           // var $titleEl = $('<' + this.titleTag + '>');
           // $titleEl.text(this.titleStr).addClass(this.titleClass);
            //this.$target.append($('<div class="heading-block">').append($titleEl));
         //   this.$target.css('width', this.widgetOptions.data_container_width);
            
            this.getRecords();
            
            return this._super();
          
        },
        
        getRecords: function() {
            // Explicitly encode the data structures to preserve during transfer 
            //alert(JSON.stringify(this.fields));
            //alert(JSON.stringify(this.domain));
            //alert(JSON.stringify(this.model));
            return $.ajax({
                url: '/website/data_slider/' + this.model,
                method: 'POST',
                data: {
                    domain: JSON.stringify(this.domain),
                    fields: JSON.stringify(this.fields),
                    limit: 10,
                },
                success: $.proxy(this.handleRecords, this),
            });
        }
      
    });
  
    return {
        defaults: defaults,
        DataSlider: sAnimation.registry.data_slider,
    };
  
});
