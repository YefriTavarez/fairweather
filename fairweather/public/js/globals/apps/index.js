'use strict'

import Vue from 'vue'
import App from './credit_mapper/App.vue'

frappe.provide("fairweather")

fairweather.CreditMapper = function () {
	this.instance = new Vue({
		el: '#app',
		render: h => h(App)
	})
};


// Path: fairweather/fairweather/public/js/globals/apps/index.js
module.exports = fairweather.CreditMapper