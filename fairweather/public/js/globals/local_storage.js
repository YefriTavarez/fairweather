// Copyright (c) 2023, Yefri Tavarez and contributors
// For license information, please see license.txt
// es-lint: disable

frappe.provide("fairweather");

fairweather.LocalStorage = class {
	constructor(namespace, temporary = true) {
		this.namespace = namespace;
		this.db = temporary? sessionStorage: localStorage;
		this.initialize_namespace();
	}

	initialize_namespace(for_reset = false) {
		this.loadStorage();

		if (
			this._data === null
			|| for_reset
		) {
			this._data = new Object();
			this.db.setItem(
				this.namespace,
				JSON.stringify(this._data),
			);
		}
	}

	commit() {
		this.db.setItem(
			this.namespace,
			JSON.stringify(this._data),
		);
	}

	rollback() {
		this.loadStorage();
	}

	loadStorage() {
		this._data = JSON.parse(
			sessionStorage.getItem(this.namespace)
		);
	}

	setValue(key, value) {
		this._data[key] = value;
		this.commit();
	}

	getValue(key, fallback = null) {
		let value = this._data[key];

		if (
			value === null
			|| value === undefined
		) {
			value = fallback;
			this.setValue(key, value);
		}

		return value;
	}
}