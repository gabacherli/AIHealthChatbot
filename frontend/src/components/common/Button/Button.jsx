import React from 'react';
import PropTypes from 'prop-types';
import './Button.css';

/**
 * Button component for user interactions
 */
const Button = ({ 
  children, 
  type = 'button', 
  variant = 'primary', 
  fullWidth = false,
  disabled = false,
  onClick,
  ...props 
}) => {
  const classNames = [
    'button',
    variant === 'secondary' ? 'secondary' : '',
    fullWidth ? 'full-width' : ''
  ].filter(Boolean).join(' ');

  return (
    <button
      type={type}
      className={classNames}
      disabled={disabled}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  );
};

Button.propTypes = {
  children: PropTypes.node.isRequired,
  type: PropTypes.oneOf(['button', 'submit', 'reset']),
  variant: PropTypes.oneOf(['primary', 'secondary']),
  fullWidth: PropTypes.bool,
  disabled: PropTypes.bool,
  onClick: PropTypes.func
};

export default Button;
