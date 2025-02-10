/* eslint-disable no-useless-escape */

import moment from 'moment';

import _ from 'lodash';

// import { REGEX } from 'app/constants';

export function isEmpty(value) {

  return value === null || value === undefined || String(value).trim() === '';

}

export function isObjectEmpty(value) {

  return Object.keys(value).length === 0 && value.constructor === Object;

}

export const getNumberOnly = (string = '') => string.replace(/[^\d]+/g, '');

export const getNumberAllowNegative = (string = '') => string.replace(/[^-?\.?\d*]+/g, '');

export const convertToNumber = (string = '') => {

  const isAlreadyNumber = typeof string === 'number';

  const isString = typeof string === 'string';

  if (isAlreadyNumber) return string;

  if (!isString) return 0;

  const numberString = getNumberOnly(string);

  return isEmpty(numberString) ? 0 : parseFloat(numberString);

};

export const convertToNumberAllowNegative = (string = '') => {

  const numberString = getNumberAllowNegative(string);

  const numberLength = numberString.length;

  if (numberLength > 1 && numberString.charAt(0) === '.') {

    return numberString.slice(1, numberLength);

  }

  if (

    (numberString.charAt(numberLength - 1) === '-' ||

      numberString.charAt(numberLength - 1) === '.') &&

    numberLength > 1

  ) {

    return numberString.slice(0, numberLength - 1);

  }

  return numberString;

};

/**

 * Get text and space only

 * for example: "walter @#$@$ngo#%#@" => "walter ngo"

 * @param str

 * @return {string}

 */

export const getTextAndSpaceOnly = (str = '') => str.replace(/[^A-Za-z\s]/g, '');

export const formatNumberWithDot = (string = '') => {

  let number = getNumberOnly(string.toString());

  if (isEmpty(number)) number = 0;

  return parseFloat(number)

    .toString()

    .replace(/(\d)(?=(\d\d\d)+(?!\d))/g, '$1.');

};

export const formatPriceNumber = (price = 0, withExt = false) => {

  const number = price.toFixed(3);

  const numberWithPoint = parseFloat(number)

    .toString()

    .replace(/(\d)(?=(\d\d\d)+(?!\d))/g, '$1,');

  return withExt ? `${numberWithPoint}.00` : `${numberWithPoint}`;

};

export const getFirstName = (string) => _.split(string, ' ', 1)[0];

export const formatDate = (date, format) => moment(date).format(format);

/**

 * Get last characters

 * @param {String} value

 * @param {Number} numberOfCharacters

 * @return {string}

 */

export const getFirstCharacters = (value = '', numberOfCharacters = 0) => {

  if (value.length > numberOfCharacters) {

    return value.slice(0, numberOfCharacters);

  }

  return value;

};

/**

 * Get last characters

 * @param {String} value

 * @param {Number} numberOfCharacters

 * @return {string}

 */

export const getLastCharacters = (value = '', numberOfCharacters = 0) => {

  if (value.length > numberOfCharacters) {

    return value.slice(-numberOfCharacters);

  }

  return value;

};

/**

 * Validate a string is an email or not

 * @param email

 * @return {boolean}

 */

// export const isEmail = (email) =>

//   /* eslint-disable no-useless-escape */

//   REGEX.email.test(String(email).toLowerCase());

/**

 * Return empty function

 */

export const noop = () => {};

export const defaultValidate = () => null;

/**

 * Convert String To Title Case <-- like this comment

 */

export const toTitleCase = (str = '') =>

  str.replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());

/**

 * to find item in collections by id

 * @param {Array} collections - format: [{ name, id }]

 * @param id

 * @return {string}

 */

export const findNameById = (collections, id) => {

  const foundItem = collections.find((item) => item.id === id);

  return foundItem ? foundItem.name : '';

};

export const checkSpecialCharacter = (str = '') => str.match(/[^A-Za-z0-9_\s]/gi) !== null;

export const transformText = (value, params = { numberOnly: false, textAndSpaceOnly: false }) => {

  if (params.numberOnly) return getNumberOnly(value);

  if (params.textAndSpaceOnly) return getTextAndSpaceOnly(value);

  return value;

};

/**

 * Verifying provided fields named -> "fieldsChecker"

 * Provided excluding mandatory fields will not be checked

 * Defining types inside the typesDefines constant,

 * if type is not supported will return default as false <- marked as an Invalid

 * @param {Object} fields - format: Object<Name: {value, type}>

 * @param {Array} excludingNotMandatoryFields - format: [string]

 * return Valid = Boolean

 */

export const typesDefine = {

  date: (date) => _.words(date, /[^\/]\d+/g).length >= 3,

  text: (text) => text.length > 0,

  number: (number) => _.isNumber(number) && _.parseInt(number) > 0,

  default: () => false

};

export const checkFieldHasValue = ({ value, type }) =>

  (!!typesDefine[type] && typesDefine[type](value)) || typesDefine.default();

export const ignoreAnyInvalidFields = (fields = []) => _.indexOf(fields, false) < 0;

export const fieldsChecker = (fields = {}, excludingNotMandatoryFields = []) => {

  const fieldsList = Object.keys(fields);

  const mandatoryFields = _.pullAllWith(fieldsList, excludingNotMandatoryFields, _.isEqual);

  return ignoreAnyInvalidFields(mandatoryFields.map((field) => checkFieldHasValue(fields[field])));

};

export const convertToFloat = (text = '') =>

  Number.isNaN(parseFloat(text)) ? text : parseFloat(text);

export const decimalToPercentage = (decimal = 0) => {

  const percentage = decimal * 100;

  return `${Math.round(percentage)}`;

};

export const percentageToDecimal = (percentage = '') => {

  const number = convertToNumber(percentage);

  const decimal = number / 100;

  return decimal;

};

export const strSplit = (string = '', separator = '') => {

  if (typeof string === 'string' && typeof separator) {

    return string.split(separator);

  }

  return [];

};

export const arrJoin = (array = [], separator = '') => {

  if (Array.isArray(array) && typeof separator === 'string') {

    return array.join(separator);

  }

  return '';

};

export const isArrayDataNotEmpty = (data) => Array.isArray(data) && data.length > 0;

export const strSplitJoin = (string = '', splitSeparator = '', joinSeparator = '') =>

  arrJoin(strSplit(string, splitSeparator), joinSeparator);

export const insertArray = (arr, index, newItem) => [

  ...arr.slice(0, index),

  newItem,

  ...arr.slice(index)

];

export const replaceArray = (arr, index, newItem) => {

  arr.splice(index, 1, newItem);

  return arr;

};

export const capitalize = (text) => {

  if (typeof text !== 'string') return '';

  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();

};

export const capitalizeTwoChar = (str = '') =>

  str

    .split(' ')

    .map((v) => capitalize(v))

    .join(' ');

export const formatInt = (int = 0) => {

  if (int < 10) {

    return `0${int}`;

  }

  return `${int}`;

};

export const formatDuration = (time = 0) => {

  const seconds = moment.duration(time).seconds();

  const minutes = moment.duration(time).minutes();

  const hours = moment.duration(time).hours();

  if (hours > 0) {

    return `${formatInt(hours)}:${formatInt(minutes)}:${formatInt(seconds)}`;

  }

  if (minutes > 0) {

    return `${formatInt(minutes)}:${formatInt(seconds)}`;

  }

  return `00:${formatInt(seconds)}`;

};

export const formatPhoneNumber = (phoneNumberString = '') => {

  const cleaned = `${getNumberOnly(phoneNumberString.toString())}`;

  const matchPhoneNumber = cleaned.match(/^(0|62|)?(\d{3})(\d{4}|\d{3})(\d{4}|\d{3})$/);

  if (matchPhoneNumber) {

    const indoCode = '+62';

    return [indoCode, matchPhoneNumber[2], matchPhoneNumber[3], matchPhoneNumber[4]].join(' ');

  }

  return phoneNumberString;

};

export const getDateTimeZone = (dateISO) => {

  const date = new Date(dateISO);

  const times = date.getTime() + date.getTimezoneOffset() * 60 * 1000;

  const dateTimeZone = new Date(times);

  return dateTimeZone;

};

export const isImage = (fileName = '') => {

  const fileExt = fileName.toLowerCase().split('.').pop();

  const imageExt = ['png', 'jpg', 'jpeg', 'bmp', 'gif', 'webp', 'psd', 'svg', 'tiff'];

  return imageExt.includes(fileExt);

};

