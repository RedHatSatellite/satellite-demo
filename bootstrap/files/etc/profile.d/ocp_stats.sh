#!/bin/sh
# vim: sw=4 ts=4 expandtab
ocpodstats ()
{
    oc adm top pod --heapster-namespace=openshift-infra --heapster-scheme=https --all-namespaces | sed 's/^NA/0A/' | sort | sed 's/^0A/NA/'
}
ocnodestats ()
{
    oc adm top node --heapster-namespace=openshift-infra --heapster-scheme=https
}
ocprojectstats ()
{
    AWK=$(cat <<'EOF'
        /^NAMESPACE/ {next}
            {sub(/m$/,"",$3); sub(/Mi *$/,"",$4)}
            {
                c[$1]+=$3;
                m[$1]+=$4;
                cc+=$3;
                mm+=$4;
            }
            END{
                for (n in c)
                    printf("%s %'d %'d\n", n, c[n], m[n])
                printf("zzzzzTOTALS %'d %'d\n", cc, mm)
            }
EOF
        )
    ocpodstats |
    awk "$AWK" | sort | sed 's/^zzzzz//' | (echo 'PROJECT CORES MEMORY(megs)';cat) | column -t
}
ocstats ()
{
    watch -n 3 "$(declare -f ocnodestats)" \; "$(declare -f ocpodstats)" \; ocnodestats \; ocpodstats
}
