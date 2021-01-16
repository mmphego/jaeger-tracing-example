# -*- mode: ruby -*-
# vi: set ft=ruby :
default_box = "opensuse/Leap-15.2.x86_64"
box_version = "15.2.31.309"
# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search.

  config.vm.define "jaeger" do |jaeger|
    jaeger.vm.box = default_box
    jaeger.vm.box_version
    jaeger.vm.hostname = "jaeger"
    jaeger.vm.network 'private_network', ip: "192.168.33.10",  virtualbox__intnet: true
    jaeger.vm.network "forwarded_port", guest: 22, host: 2222, id: "ssh", disabled: true
    jaeger.vm.network "forwarded_port", guest: 22, host: 2000 # Master Node SSH
    jaeger.vm.network "forwarded_port", guest: 6443, host: 6443 # API Access
    for p in 30000..30100 # expose NodePort IP's
      jaeger.vm.network "forwarded_port", guest: p, host: p, protocol: "tcp"
    end
    jaeger.vm.provider "virtualbox" do |vb|
      # v.memory = "3072"
      vb.memory = "2048"
      vb.name = "jaeger"
    end

    jaeger.vm.provision "shell", inline: <<-SHELL
      echo "******** Installing dependencies ********"
      sudo zypper refresh
      sudo zypper --quite --non-interactive install bzip2
      sudo zypper --quite --non-interactive install etcd
      sudo zypper --quite --non-interactive install lsof

      echo "******** Begin installing k3s ********"
      curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.19.2+k3s1 K3S_KUBECONFIG_MODE="644" sh -
      echo "******** End installing k3s ********"

      echo "******** Begin installing jaeger ********"
      /usr/local/bin/kubectl create namespace observability
      /usr/local/bin/kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/crds/jaegertracing.io_jaegers_crd.yaml
      /usr/local/bin/kubectl create -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/service_account.yaml
      /usr/local/bin/kubectl create -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/role.yaml
      /usr/local/bin/kubectl create -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/role_binding.yaml
      /usr/local/bin/kubectl create -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/operator.yaml
      echo "******** End installing jaeger ********"

      echo "******** Verify jaeger is running ********"
      /usr/local/bin/kubectl get pods --namespace=observability
    SHELL
  end
end
