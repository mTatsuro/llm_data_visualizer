// Simple JS "types" via JSDoc comments for editor hints only.

/**
 * @typedef {"pie" | "scatter" | "table"} VizType
 */

/**
 * @typedef {Object} Encoding
 * @property {string} [x]
 * @property {string} [y]
 * @property {string} [label]
 * @property {string[]} [tooltip]
 * @property {string} [value]
 */

/**
 * @typedef {Object} Style
 * @property {string} [color]
 * @property {boolean} [header_bold]
 * @property {string} [title]
 */

/**
 * @typedef {Object} Visualization
 * @property {string} viz_id
 * @property {VizType} viz_type
 * @property {any[]} data
 * @property {Encoding} encoding
 * @property {Style} style
 * @property {any[]} [transforms]
 * @property {Object} [insights]
 */
