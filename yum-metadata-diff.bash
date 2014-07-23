# bash completion for yum-metadata-diff

_yum_metadata_diff()
{
    COMPREPLY=()
    if [[ $2 == -* ]] ; then
        COMPREPLY=( $( compgen -W '--help --check --compare --verbose' -- "$2" ) )
    else
        COMPREPLY=( $( compgen -f -- "$2" ) )
    fi
} &&
complete -F _yum_metadata_diff -o filenames yum-metadata-diff

# Local variables:
# mode: shell-script
# sh-basic-offset: 4
# sh-indent-comment: t
# indent-tabs-mode: nil
# End:
# ex: ts=4 sw=4 et filetype=sh
