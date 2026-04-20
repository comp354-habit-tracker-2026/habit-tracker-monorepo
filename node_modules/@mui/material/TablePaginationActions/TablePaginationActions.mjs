'use client';

import * as React from 'react';
import PropTypes from 'prop-types';
import { useRtl } from '@mui/system/RtlProvider';
import composeClasses from '@mui/utils/composeClasses';
import clsx from 'clsx';
import { styled } from "../zero-styled/index.mjs";
import { useDefaultProps } from "../DefaultPropsProvider/index.mjs";
import KeyboardArrowLeft from "../internal/svg-icons/KeyboardArrowLeft.mjs";
import KeyboardArrowRight from "../internal/svg-icons/KeyboardArrowRight.mjs";
import IconButton from "../IconButton/index.mjs";
import LastPageIconDefault from "../internal/svg-icons/LastPage.mjs";
import FirstPageIconDefault from "../internal/svg-icons/FirstPage.mjs";
import { getTablePaginationActionsUtilityClass } from "./tablePaginationActionsClasses.mjs";
import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
const useUtilityClasses = ownerState => {
  const {
    classes
  } = ownerState;
  const slots = {
    root: ['root']
  };
  return composeClasses(slots, getTablePaginationActionsUtilityClass, classes);
};
const TablePaginationActionsRoot = styled('div', {
  name: 'MuiTablePaginationActions',
  slot: 'Root'
})({});
const TablePaginationActions = /*#__PURE__*/React.forwardRef(function TablePaginationActions(inProps, ref) {
  const props = useDefaultProps({
    props: inProps,
    name: 'MuiTablePaginationActions'
  });
  const {
    className,
    count,
    disabled = false,
    getItemAriaLabel,
    onPageChange,
    page,
    rowsPerPage,
    showFirstButton,
    showLastButton,
    slots = {},
    slotProps = {},
    ...other
  } = props;
  const isRtl = useRtl();
  const ownerState = props;
  const classes = useUtilityClasses(ownerState);
  const handleFirstPageButtonClick = event => {
    onPageChange(event, 0);
  };
  const handleBackButtonClick = event => {
    onPageChange(event, page - 1);
  };
  const handleNextButtonClick = event => {
    onPageChange(event, page + 1);
  };
  const handleLastPageButtonClick = event => {
    onPageChange(event, Math.max(0, Math.ceil(count / rowsPerPage) - 1));
  };
  const FirstButton = slots.firstButton ?? IconButton;
  const LastButton = slots.lastButton ?? IconButton;
  const NextButton = slots.nextButton ?? IconButton;
  const PreviousButton = slots.previousButton ?? IconButton;
  const FirstButtonIcon = slots.firstButtonIcon ?? FirstPageIconDefault;
  const LastButtonIcon = slots.lastButtonIcon ?? LastPageIconDefault;
  const NextButtonIcon = slots.nextButtonIcon ?? KeyboardArrowRight;
  const PreviousButtonIcon = slots.previousButtonIcon ?? KeyboardArrowLeft;
  const FirstButtonSlot = isRtl ? LastButton : FirstButton;
  const PreviousButtonSlot = isRtl ? NextButton : PreviousButton;
  const NextButtonSlot = isRtl ? PreviousButton : NextButton;
  const LastButtonSlot = isRtl ? FirstButton : LastButton;
  const firstButtonSlotProps = isRtl ? slotProps.lastButton : slotProps.firstButton;
  const previousButtonSlotProps = isRtl ? slotProps.nextButton : slotProps.previousButton;
  const nextButtonSlotProps = isRtl ? slotProps.previousButton : slotProps.nextButton;
  const lastButtonSlotProps = isRtl ? slotProps.firstButton : slotProps.lastButton;
  return /*#__PURE__*/_jsxs(TablePaginationActionsRoot, {
    ref: ref,
    className: clsx(classes.root, className),
    ...other,
    children: [showFirstButton && /*#__PURE__*/_jsx(FirstButtonSlot, {
      onClick: handleFirstPageButtonClick,
      disabled: disabled || page === 0,
      "aria-label": getItemAriaLabel('first', page),
      title: getItemAriaLabel('first', page),
      ...firstButtonSlotProps,
      children: isRtl ? /*#__PURE__*/_jsx(LastButtonIcon, {
        ...slotProps.lastButtonIcon
      }) : /*#__PURE__*/_jsx(FirstButtonIcon, {
        ...slotProps.firstButtonIcon
      })
    }), /*#__PURE__*/_jsx(PreviousButtonSlot, {
      onClick: handleBackButtonClick,
      disabled: disabled || page === 0,
      color: "inherit",
      "aria-label": getItemAriaLabel('previous', page),
      title: getItemAriaLabel('previous', page),
      ...previousButtonSlotProps,
      children: isRtl ? /*#__PURE__*/_jsx(NextButtonIcon, {
        ...slotProps.nextButtonIcon
      }) : /*#__PURE__*/_jsx(PreviousButtonIcon, {
        ...slotProps.previousButtonIcon
      })
    }), /*#__PURE__*/_jsx(NextButtonSlot, {
      onClick: handleNextButtonClick,
      disabled: disabled || (count !== -1 ? page >= Math.ceil(count / rowsPerPage) - 1 : false),
      color: "inherit",
      "aria-label": getItemAriaLabel('next', page),
      title: getItemAriaLabel('next', page),
      ...nextButtonSlotProps,
      children: isRtl ? /*#__PURE__*/_jsx(PreviousButtonIcon, {
        ...slotProps.previousButtonIcon
      }) : /*#__PURE__*/_jsx(NextButtonIcon, {
        ...slotProps.nextButtonIcon
      })
    }), showLastButton && /*#__PURE__*/_jsx(LastButtonSlot, {
      onClick: handleLastPageButtonClick,
      disabled: disabled || page >= Math.ceil(count / rowsPerPage) - 1,
      "aria-label": getItemAriaLabel('last', page),
      title: getItemAriaLabel('last', page),
      ...lastButtonSlotProps,
      children: isRtl ? /*#__PURE__*/_jsx(FirstButtonIcon, {
        ...slotProps.firstButtonIcon
      }) : /*#__PURE__*/_jsx(LastButtonIcon, {
        ...slotProps.lastButtonIcon
      })
    })]
  });
});
process.env.NODE_ENV !== "production" ? TablePaginationActions.propTypes /* remove-proptypes */ = {
  // ┌────────────────────────────── Warning ──────────────────────────────┐
  // │ These PropTypes are generated from the TypeScript type definitions. │
  // │    To update them, edit the d.ts file and run `pnpm proptypes`.     │
  // └─────────────────────────────────────────────────────────────────────┘
  /**
   * @ignore
   */
  children: PropTypes.node,
  /**
   * Override or extend the styles applied to the component.
   */
  classes: PropTypes.object,
  /**
   * @ignore
   */
  className: PropTypes.string,
  /**
   * @ignore
   */
  count: PropTypes.number.isRequired,
  /**
   * If `true`, the component is disabled.
   * @default false
   */
  disabled: PropTypes.bool,
  /**
   * Accepts a function which returns a string value that provides a user-friendly name for the current page.
   * This is important for screen reader users.
   *
   * For localization purposes, you can use the provided [translations](https://mui.com/material-ui/guides/localization/).
   * @param {string} type The link or button type to format ('first' | 'last' | 'next' | 'previous').
   * @returns {string}
   */
  getItemAriaLabel: PropTypes.func.isRequired,
  /**
   * @ignore
   */
  onPageChange: PropTypes.func.isRequired,
  /**
   * @ignore
   */
  page: PropTypes.number.isRequired,
  /**
   * @ignore
   */
  rowsPerPage: PropTypes.number.isRequired,
  /**
   * @ignore
   */
  showFirstButton: PropTypes.bool.isRequired,
  /**
   * @ignore
   */
  showLastButton: PropTypes.bool.isRequired,
  /**
   * @ignore
   */
  slotProps: PropTypes.shape({
    firstButton: PropTypes.object,
    firstButtonIcon: PropTypes.object,
    lastButton: PropTypes.object,
    lastButtonIcon: PropTypes.object,
    nextButton: PropTypes.object,
    nextButtonIcon: PropTypes.object,
    previousButton: PropTypes.object,
    previousButtonIcon: PropTypes.object
  }),
  /**
   * @ignore
   */
  slots: PropTypes.shape({
    firstButton: PropTypes.elementType,
    firstButtonIcon: PropTypes.elementType,
    lastButton: PropTypes.elementType,
    lastButtonIcon: PropTypes.elementType,
    nextButton: PropTypes.elementType,
    nextButtonIcon: PropTypes.elementType,
    previousButton: PropTypes.elementType,
    previousButtonIcon: PropTypes.elementType
  })
} : void 0;
export default TablePaginationActions;