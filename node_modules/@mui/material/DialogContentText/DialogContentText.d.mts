import * as React from 'react';
import { SxProps } from '@mui/system';
import { TypographyTypeMap } from "../Typography/index.mjs";
import { OverrideProps, OverridableComponent } from "../OverridableComponent/index.mjs";
import { Theme } from "../styles/index.mjs";
import { DialogContentTextClasses } from "./dialogContentTextClasses.mjs";
export interface DialogContentTextOwnProps extends Omit<TypographyTypeMap['props'], 'classes'> {
  /**
   * Override or extend the styles applied to the component.
   */
  classes?: Partial<DialogContentTextClasses> | undefined;
  /**
   * The system prop that allows defining system overrides as well as additional CSS styles.
   */
  sx?: SxProps<Theme> | undefined;
}
export interface DialogContentTextTypeMap<AdditionalProps = {}, RootComponent extends React.ElementType = TypographyTypeMap['defaultComponent']> {
  props: AdditionalProps & DialogContentTextOwnProps;
  defaultComponent: RootComponent;
}

/**
 *
 * Demos:
 *
 * - [Dialog](https://mui.com/material-ui/react-dialog/)
 *
 * API:
 *
 * - [DialogContentText API](https://mui.com/material-ui/api/dialog-content-text/)
 * - inherits [Typography API](https://mui.com/material-ui/api/typography/)
 */
declare const DialogContentText: OverridableComponent<DialogContentTextTypeMap>;
export type DialogContentTextProps<RootComponent extends React.ElementType = DialogContentTextTypeMap['defaultComponent'], AdditionalProps = {}> = OverrideProps<DialogContentTextTypeMap<AdditionalProps, RootComponent>, RootComponent> & {
  component?: React.ElementType | undefined;
};
export default DialogContentText;