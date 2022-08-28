// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// MIT License. See license.txt

// for translation
finergy._ = function(txt, replace, context = null) {
	if (!txt) return txt;
	if (typeof txt != "string") return txt;

	let translated_text = '';

	let key = txt;    // txt.replace(/\n/g, "");
	if (context) {
		translated_text = finergy._messages[`${key}:${context}`];
	}

	if (!translated_text) {
		translated_text = finergy._messages[key] || txt;
	}

	if (replace && typeof replace === "object") {
		translated_text = $.format(translated_text, replace);
	}
	return translated_text;
};

window.__ = finergy._;

finergy.get_languages = function() {
	if (!finergy.languages) {
		finergy.languages = [];
		$.each(finergy.boot.lang_dict, function(lang, value) {
			finergy.languages.push({ label: lang, value: value });
		});
		finergy.languages = finergy.languages.sort(function(a, b) {
			return a.value < b.value ? -1 : 1;
		});
	}
	return finergy.languages;
};
